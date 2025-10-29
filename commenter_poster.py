import os
import time
from typing import Tuple, Optional, List
import requests
import json
from dotenv import load_dotenv

# optional agent imports (used to generate comments when requested)
try:
    from comment_agent import get_comment_agent
    from crewai import Crew, Task
except Exception:
    get_comment_agent = None
    Crew = None
    Task = None

load_dotenv()

def post_comment_to_post(post_id: str, page_access_token: str, message: str, api_version: str = "v18.0") -> Tuple[bool, str]:
    """Post a comment to a Facebook post (post_id) using the Page access token.

    Returns (True, comment_id) on success or (False, error_message) on failure.
    """
    url = f"https://graph.facebook.com/{api_version}/{post_id}/comments"
    payload = {"message": message, "access_token": page_access_token}
    try:
        resp = requests.post(url, data=payload, timeout=20)
    except Exception as e:
        return False, f"Network error when posting comment: {e}"

    try:
        data = resp.json()
    except Exception:
        return False, f"Non-JSON response: {resp.text}"

    if resp.status_code >= 400:
        err = data.get("error") or data
        return False, f"Graph API error: {json.dumps(err)}"

    comment_id = data.get("id") or json.dumps(data)
    return True, comment_id

def generate_comment_for_url(url: str, topics: List[str], excerpt: Optional[str] = None, max_words: int = 60) -> Tuple[bool, str]:
    """Use the Comment Agent to generate a short comment for the given URL and topics.

    Returns (True, comment_text) or (False, error_message).
    If the comment agent is not available, returns False.
    """
    if get_comment_agent is None or Crew is None or Task is None:
        return False, "Comment agent or Crew not available in this environment"

    try:
        agent = get_comment_agent()
        topic_text = ", ".join(topics) if topics else ""
        excerpt_text = (excerpt[:800] + "...") if excerpt else ""

        desc = (
            f"You are a concise comment-writer. Write a short, natural, human-sounding comment (1-2 sentences, ~30-60 words) for the article at {url}."
            f" The comment should reference the following topics: {topic_text}."
            f" Article excerpt: {excerpt_text}\n\n"
            "Important: Output ONLY the comment text. No headings or extra commentary."
        )

        task = Task(description=desc, agent=agent, expected_output="Short comment text")
        crew = Crew(agents=[agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        # extract output (mirror the extraction used in the Streamlit UI)
        out = ""
        if hasattr(result, 'tasks_output') and result.tasks_output:
            to = result.tasks_output[0]
            out = getattr(to, 'raw', None) or getattr(to, 'exported_output', None) or str(to)
        else:
            # fall back to str(result)
            out = str(result)

        # basic cleanup
        out = out.strip()
        return True, out
    except Exception as e:
        return False, f"Failed to generate comment: {e}"

def create_page_post_and_comment(
    page_id: str,
    page_access_token: str,
    url: str,
    topics: List[str],
    excerpt: Optional[str] = None,
    comment_text: Optional[str] = None,
    include_comment_in_post: bool = True,
    post_as_comment: bool = True,
    api_version: str = "v18.0",
) -> Tuple[bool, str]:
    """High-level helper:
    1) Optionally generate a personalized comment for the URL (unless comment_text provided)
    2) Create a Page post linking to `url`. If include_comment_in_post is True, the post message will
       include the personalized comment so it appears in the post body (useful for shares where you
       want commentary shown alongside the link preview).
    3) Post the generated comment as a comment on the created Page post as well.

    Returns (True, details) on success where details include post_id and comment_id.
    """
    # 1) Generate or use provided comment
    if not comment_text:
        gen_ok, comment_or_err = generate_comment_for_url(url, topics, excerpt)
        if not gen_ok:
            return False, f"Failed to generate comment: {comment_or_err}"
        comment_text = comment_or_err

    # 2) Prepare post message
    if include_comment_in_post and comment_text:
        message = comment_text
        if topics:
            # append a short topics line if helpful
            message = f"{comment_text}\n\nTopics: {', '.join(topics)}"
    else:
        message = f"Sharing an interesting article about: {', '.join(topics)}"

    success, result = post_to_facebook_page(page_id, page_access_token, message=message, link=url, api_version=api_version)
    if not success:
        return False, f"Failed to create page post: {result}"

    post_id = result

    # 3) Optionally post the comment to the created post as a separate comment
    comment_id_or_err = None
    if post_as_comment and comment_text:
        ok, comment_id_or_err = post_comment_to_post(post_id, page_access_token, comment_text, api_version=api_version)
        if not ok:
            return False, f"Post created ({post_id}) but failed to post comment: {comment_id_or_err}"

    return True, json.dumps({"post_id": post_id, "comment_id": comment_id_or_err})

def debug_facebook_token(token: str, app_token: Optional[str] = None, api_version: str = "v18.0") -> dict:
    """Call the Graph API debug_token endpoint to inspect an access token.

    - token: the token you want to debug (user or page token)
    - app_token: optional app access token (app_id|app_secret) or other token with inspection rights.
      If not provided, this function will try to build one from environment variables
      `FB_APP_ID` and `FB_APP_SECRET` as `app_id|app_secret`.
    Returns the parsed JSON response (or raises an exception on HTTP error).
    """
    if app_token is None:
        app_id = os.getenv("FB_APP_ID")
        app_secret = os.getenv("FB_APP_SECRET")
        if app_id and app_secret:
            app_token = f"{app_id}|{app_secret}"
        else:
            raise RuntimeError("No app_token provided and FB_APP_ID/FB_APP_SECRET not set in env")

    url = f"https://graph.facebook.com/{api_version}/debug_token"
    params = {"input_token": token, "access_token": app_token}
    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def post_to_facebook_page(page_id: str, page_access_token: str, message: str, link: Optional[str] = None, api_version: str = "v18.0") -> Tuple[bool, str]:
    """Post a message (optionally with a link) to a Facebook Page using the Graph API.

    Returns (True, post_id) on success or (False, error_message) on failure.

    Requirements:
    - The `page_access_token` must be a valid Page access token with `pages_manage_posts`.
    - The app may need App Review and the Page must grant the token.

    Example:
        success, result = post_to_facebook_page(PAGE_ID, PAGE_TOKEN, "Check this out", "https://example.com")
    """
    url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
    payload = {"message": message, "access_token": page_access_token}
    if link:
        # adding a `link` makes Facebook create a link preview (if the URL is fetchable)
        payload["link"] = link

    try:
        resp = requests.post(url, data=payload, timeout=20)
    except Exception as e:
        return False, f"Network error when calling Graph API: {e}"

    try:
        data = resp.json()
    except Exception:
        return False, f"Non-JSON response: {resp.text}"

    if resp.status_code >= 400:
        # Graph API error structure: {"error": {"message":..., "type":..., "code":..., "error_subcode":...}}
        err = data.get("error") or data
        return False, f"Graph API error: {json.dumps(err)}"

    # success response contains the id of the created post (e.g., "{page_id}_{post_id}")
    post_id = data.get("id") or json.dumps(data)
    return True, post_id


def get_page_token_from_user_token(user_token: str, target_page_id: Optional[str] = None, api_version: str = "v18.0") -> Tuple[bool, str]:
    """If you have a USER access token (short or long lived), call /me/accounts to retrieve
    the Page access token for a Page the user manages.

    Returns (True, page_token) or (False, error_message).
    If target_page_id is provided, returns the token for that page, otherwise returns the first page token found.
    """
    url = f"https://graph.facebook.com/{api_version}/me/accounts"
    params = {"access_token": user_token}
    try:
        resp = requests.get(url, params=params, timeout=20)
    except Exception as e:
        return False, f"Network error when calling /me/accounts: {e}"

    try:
        data = resp.json()
    except Exception:
        return False, f"Non-JSON response: {resp.text}"

    if resp.status_code >= 400:
        err = data.get("error") or data
        return False, f"Graph API error: {json.dumps(err)}"

    pages = data.get("data", [])
    if not pages:
        return False, "No managed pages found for this user token"

    if target_page_id:
        for p in pages:
            if str(p.get("id")) == str(target_page_id):
                return True, p.get("access_token")
        return False, f"User token does not grant access to page id {target_page_id}"

    # return first page token
    first = pages[0]
    return True, first.get("access_token")


# Selenium/ChromeDriver-based posting has been removed for safety and stability.
# The library now supports simulated posting (safe) and Facebook Page posting via Graph API.


def post_comment(website_url: str, comment_text: str) -> Tuple[bool, str]:
    """(removed) Posting directly to arbitrary websites has been removed.

    This function was intentionally deleted to prevent accidental posting to external
    websites. Use the Facebook Page posting helpers (`create_page_post_and_comment`) for
    authorized publishing to Pages.
    """
    raise NotImplementedError("Direct posting to arbitrary websites has been removed.")
