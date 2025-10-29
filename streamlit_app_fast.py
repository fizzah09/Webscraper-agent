from crewai import Crew, Task
from crawleragent import get_crawler_agent, search_duckduckgo, search_bing
from cleaneragent import get_cleaner_agent
from analyzer_agent import get_analyzer_agent
from sentiment_agent import get_sentiment_agent
from reporter_agent import get_reporter_agent
from comment_agent import get_comment_agent
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import streamlit as st
import json
from sentiment_utils import analyze_sentiment_for_urls
import os
import warnings
import re
warnings.filterwarnings("ignore")
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
st.set_page_config(
    page_title="CrewAI Blog Analyzer & Commenter",
    page_icon="😁",
    layout="wide"
)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .agent-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #1E88E5;
        background-color: #E3F2FD;
    }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="main-header">CrewAI Blog Analyzer & Comment Generator</div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🚀 Agent Pipeline")
    st.markdown("---")
    
    st.write("**6 AI Agents Working Together:**")
    st.write("1. 🕷️ Crawler - Finds blogs")
    st.write("2. 🧹 Cleaner - Cleans text")
    st.write("3. 🔍 Analyzer - Extracts topics")
    st.write("4. 😊 Sentiment - Detects emotions")
    st.write("5. 📝 Reporter - Creates report")
    st.write("6. 💬 Commenter - Writes comment")
    
    st.markdown("---")
    st.info("**LLM:** OpenRouter GPT-4o-mini")

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'result_text' not in st.session_state:
    st.session_state.result_text = ""
if 'crawler_text' not in st.session_state:
    st.session_state.crawler_text = ""
if 'cleaner_text' not in st.session_state:
    st.session_state.cleaner_text = ""
if 'analyzer_text' not in st.session_state:
    st.session_state.analyzer_text = ""
if 'sentiment_text' not in st.session_state:
    st.session_state.sentiment_text = ""
if 'report_text' not in st.session_state:
    st.session_state.report_text = ""
if 'comment_text' not in st.session_state:
    st.session_state.comment_text = ""
if 'keyword' not in st.session_state:
    st.session_state.keyword = ""

st.markdown("### 🔍 Enter a keyword to analyze blog posts")
keyword = st.text_input(
    "Keyword:",
    placeholder="e.g., artificial intelligence, climate change, cryptocurrency",
    label_visibility="collapsed"
)
num_results = st.number_input("Number of blogs to find:", min_value=1, max_value=50, value=5, step=1, help="How many search results to collect and analyze")

analyze_button = st.button(" Start Analysis & Generate Comment", type="primary", use_container_width=True)

# Pre-check for LLM API keys to avoid confusing crewai/LLM initialization errors
llm_present = bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"))
if not llm_present:
    st.error(
        "Missing LLM API key: set either OPENAI_API_KEY or OPENROUTER_API_KEY in your environment (or .env).\n"
        "Without a valid key the agents cannot initialize.\n"
        "Troubleshooting: verify your .env, activate your conda env, and restart Streamlit."
    )
    st.stop()

# Show currently discovered URLs (updates during analysis)
with st.sidebar.expander("🔎 Discovered URLs (live)", expanded=False):
    urls_sidebar = st.session_state.get('crawler_urls', [])
    if urls_sidebar:
        for u in urls_sidebar:
            st.markdown(f"- [{u}]({u})")
    else:
        st.markdown("_(no URLs discovered yet)_")

# Inline short preview of discovered URLs (updates during analysis)
urls_preview_inline = st.session_state.get('crawler_urls', [])
if urls_preview_inline:
    st.markdown("### 🔗 Discovered URLs")
    for u in urls_preview_inline:
        st.markdown(f"- [{u}]({u})")

if analyze_button and keyword:
    st.session_state.keyword = keyword
    st.session_state.analysis_complete = False
    st.markdown("---")
    st.markdown(f"### 📊 Analyzing: **{keyword}**")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    agent_containers = {}
    for i in range(6):
        agent_containers[i] = st.empty()
    
    try:
        status_text.info("⭐Initializing AI agents...")
        
        CrawlerAgent = get_crawler_agent()
        CleanerAgent = get_cleaner_agent()
        AnalyzerAgent = get_analyzer_agent()
        SentimentAgent = get_sentiment_agent()
        ReporterAgent = get_reporter_agent()
        CommentAgent = get_comment_agent()
        
        tasks = []

        # Run a deterministic web search to get real URLs for the keyword (prefer DuckDuckGo, fallback to Bing)
        try:
            urls = search_duckduckgo(keyword, max_results=num_results)
            if not urls:
                urls = search_bing(keyword, max_results=num_results)
            # resolve redirects to show clean target URLs
            try:
                from crawleragent import resolve_final_urls
                urls = resolve_final_urls(urls)
            except Exception:
                pass
            st.session_state.crawler_text = "\n".join(urls) if urls else ""
            st.session_state.crawler_urls = urls
            if urls:
                st.session_state.sentiment_results = analyze_sentiment_for_urls(urls)
                lines = [f"{item.get('label','unknown').upper()} ({item.get('polarity')}) - {item.get('url')}" for item in st.session_state.sentiment_results]
                st.session_state.sentiment_text = "\n".join(lines)
            else:
                st.session_state.sentiment_results = []

            # Immediately show discovered URLs and per-URL sentiment so the user sees findings
            try:
                urls_preview = st.session_state.get('crawler_urls', [])
                sr_preview = st.session_state.get('sentiment_results', [])
                if urls_preview:
                    st.markdown("### 🔎 Discovered blogs & per-URL sentiment")
                    for item in sr_preview:
                        url = item.get('url')
                        label = item.get('label', 'unknown')
                        pol = item.get('polarity')
                        subj = item.get('subjectivity')
                        excerpt = item.get('excerpt', '')
                        st.markdown(f"- **{label.upper()}** — ({pol}, subj={subj}) — [{url}]({url})")
                        if excerpt:
                            st.text(excerpt[:400] + ("..." if len(excerpt) > 400 else ""))
                    st.markdown('---')
            except Exception:
                # non-critical; continue without blocking analysis
                pass
        except Exception:
            st.session_state.crawler_urls = st.session_state.get('crawler_urls', [])
            st.session_state.sentiment_results = st.session_state.get('sentiment_results', [])
        
        agent_containers[0].markdown(
            '<div class="agent-box">🕷️ <b>Crawler Agent:</b> Searching for blog posts...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.15)
        
        crawl_task = Task(
            description=f"Search and find blog posts about '{keyword}'. Provide a summary of the content found.",
            agent=CrawlerAgent,
            expected_output="Summary of blog posts found about the topic"
        )
        tasks.append(crawl_task)
        
        agent_containers[1].markdown(
            '<div class="agent-box">🧹 <b>Cleaner Agent:</b> Cleaning and processing text...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.3)
        
        clean_task = Task(
            description="Clean and normalize the text content. Remove noise and prepare for analysis.",
            agent=CleanerAgent,
            expected_output="Clean, normalized text ready for analysis"
        )
        tasks.append(clean_task)
        
        agent_containers[2].markdown(
            '<div class="agent-box">🔍 <b>Analyzer Agent:</b> Analyzing topics and themes...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.45)
        
        analyze_task = Task(
            description=f"Analyze the content about '{keyword}'. Identify key topics, themes, and main ideas.",
            agent=AnalyzerAgent,
            expected_output="Key topics, themes, and insights from the content"
        )
        tasks.append(analyze_task)
        
        agent_containers[3].markdown(
            '<div class="agent-box">😊 <b>Sentiment Agent:</b> Detecting emotional tone...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.6)
        
        sentiment_task = Task(
            description="Analyze the sentiment and emotional tone of the content. Determine if it's positive, negative, or neutral.",
            agent=SentimentAgent,
            expected_output="Sentiment analysis with emotional tone classification"
        )
        tasks.append(sentiment_task)
        
        agent_containers[4].markdown(
            '<div class="agent-box">📝 <b>Reporter Agent:</b> Generating comprehensive report...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.75)

        sentiment_summary = ""
        try:
            sr = st.session_state.get('sentiment_results', [])
            if sr:
                sentiment_summary = json.dumps(sr, ensure_ascii=False, indent=2)
        except Exception:
            sentiment_summary = str(st.session_state.get('sentiment_text', ''))

        crawler_urls_text = "\n".join(st.session_state.get('crawler_urls', []))

        report_task = Task(
            description=(
                f"Create a comprehensive analysis report about '{keyword}' combining all findings.\n"
                f"Include the following detected source URLs:\n{crawler_urls_text}\n\n"
                f"Per-URL sentiment data (polarity/subjectivity/label):\n{sentiment_summary}\n\n"
                "Use the Analyzer and Sentiment outputs to produce a single, well-structured report"
            ),
            agent=ReporterAgent,
            expected_output="Detailed analysis report with all insights"
        )
        tasks.append(report_task)
        
        agent_containers[5].markdown(
            '<div class="agent-box">💬 <b>Comment Agent:</b> Crafting personalized comment...</div>',
            unsafe_allow_html=True
        )
        progress_bar.progress(0.9)
        
        comment_task = Task(
            description=f"""Based on ALL the analysis done on '{keyword}', write a SHORT blog comment (2-3 sentences max).
            
            IMPORTANT: Output ONLY the comment text itself. Do NOT include:
            - Headers or titles
            - Explanations about what you're doing
            - Analysis or reports
            - Any markdown formatting
            
            The comment should:
            - Be exactly 2-3 sentences (40-60 words total)
            - Sound like a real person commenting on a blog
            - Reflect the sentiment found in the analysis
            - Be conversational and engaging
            - Be ready to copy-paste directly onto a blog
            
            Example format: "This is fascinating! The insights on [topic] really highlight [point]. Looking forward to seeing how this develops."
            
            Write ONLY the comment, nothing else.""",
            agent=CommentAgent,
            expected_output="A short 2-3 sentence blog comment, nothing else"
        )
        tasks.append(comment_task)
        
        status_text.info("Running multi-agent analysis...")
        
        crew = Crew(
            agents=[CrawlerAgent, CleanerAgent, AnalyzerAgent, SentimentAgent, ReporterAgent, CommentAgent],
            tasks=tasks,
            verbose=False
        )
        
        result = crew.kickoff()
        
        for i in range(6):
            agent_names = ["🕷️ Crawler", "🧹 Cleaner", "🔍 Analyzer", "😊 Sentiment", "📝 Reporter", "💬 Commenter"]
            agent_containers[i].markdown(
                f'<div class="agent-box"><b>{agent_names[i]} Agent:</b> ✅ Completed</div>',
                unsafe_allow_html=True
            )
        
        progress_bar.progress(1.0)
        status_text.success("✅ Analysis Complete!")
        

        def get_task_output(task_index):
            try:
                if hasattr(result, 'tasks_output') and len(result.tasks_output) > task_index:
                    task_out = result.tasks_output[task_index]
                    if hasattr(task_out, 'raw'):
                        return str(task_out.raw)
                    elif hasattr(task_out, 'exported_output'):
                        return str(task_out.exported_output)
                    else:
                        return str(task_out)
                elif len(tasks) > task_index:
                    task = tasks[task_index]
                    if hasattr(task, 'output') and task.output:
                        if hasattr(task.output, 'raw'):
                            return str(task.output.raw)
                        elif hasattr(task.output, 'exported_output'):
                            return str(task.output.exported_output)
                        else:
                            return str(task.output)
            except Exception as e:
                return ""
            return ""
        
        crawler_output = get_task_output(0)
        cleaner_output = get_task_output(1)
        analyzer_output = get_task_output(2)
        sentiment_output = get_task_output(3)
        report_output = get_task_output(4)
        comment_output = get_task_output(5)
        
        full_result = str(result)
        st.session_state.result_text = full_result
        st.session_state.crawler_text = crawler_output
        st.session_state.cleaner_text = cleaner_output
        st.session_state.analyzer_text = analyzer_output
        st.session_state.sentiment_text = sentiment_output
        # sentiment results are prepared earlier via search_duckduckgo and sentiment_utils
        st.session_state.report_text = report_output  
        st.session_state.comment_text = comment_output  
        st.session_state.analysis_complete = True
        
        st.rerun()
        
    except Exception as e:
        status_text.error(f"❌ Error: {str(e)}")
        st.error("**Troubleshooting:**\n- Verify .env has OPENROUTER_API_KEY\n- Check conda environment is activated\n- Ensure internet connection")

elif st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown(f"### 📊 Analysis Results for: **{st.session_state.keyword}**")
    
    result_text = st.session_state.result_text
    
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Generated Comment", "📈 Insights", "☁️ Word Cloud", "📄 Full Report"])
    
    with tab1:
        st.markdown("### 💬 AI-Generated Comment")
        
        generated_comment = st.session_state.get('comment_text', "")
        
        if generated_comment:
            generated_comment = re.sub(r'^(Comment:|Answer:|Final Answer:)\s*', '', generated_comment, flags=re.IGNORECASE)
            sentences = re.split(r'[.!?]+', generated_comment)
            clean_sentences = []
            for sent in sentences[:3]:
                cleaned = sent.strip()
                if cleaned and len(cleaned) > 15:
                    clean_sentences.append(cleaned)
            if clean_sentences:
                generated_comment = '. '.join(clean_sentences) + '.'
        
        if not generated_comment or len(generated_comment) < 30:
            if "positive" in result_text.lower() or "optimis" in result_text.lower():
                generated_comment = f"This is a fascinating analysis of {st.session_state.keyword}! The positive outlook and comprehensive examination really showcase the transformative potential. I particularly appreciate the balanced perspective on both opportunities and ethical considerations."
            elif "negative" in result_text.lower() or "concern" in result_text.lower():
                generated_comment = f"Thank you for this thoughtful analysis on {st.session_state.keyword}. The concerns and challenges highlighted are crucial considerations. Your examination of the ethical implications provides valuable insights for navigating this complex landscape."
            else:
                generated_comment = f"Excellent insights on {st.session_state.keyword}! This comprehensive analysis captures the multifaceted nature of the topic beautifully. The interdisciplinary approach makes this a truly valuable resource."
        
        generated_comment = generated_comment.strip()
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; box-shadow: 0 8px 16px rgba(0,0,0,0.2); margin: 1rem 0;">
            <h3 style="color: white; margin-top: 0;">💬 Your Personalized Blog Comment:</h3>
            <p style="font-size: 1.15rem; line-height: 1.8; margin-top: 1rem; color: white; font-style: italic;">
                "{generated_comment}"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📋 Copy Comment",
                data=generated_comment,
                file_name="blog_comment.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_comment"
            )
        
        with col2:
            # Target posting UI removed. Posting to arbitrary external sites is disabled.
            st.info("Posting to arbitrary external sites has been removed from this UI for safety. Use the Facebook Page flow to publish posts including your generated comment.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📣 Post to Facebook Page")
    # Support both FB_PAGE_* and legacy FACEBOOK_* env var names
    default_fb_id = os.getenv("FB_PAGE_ID") or os.getenv("FACEBOOK_ID") or ""
    default_fb_token = os.getenv("FB_PAGE_TOKEN") or os.getenv("FACEBOOK_TOKEN") or ""
    fb_page_id = st.text_input("Facebook Page ID:", value=default_fb_id, help="Page ID to post to")
    fb_page_token = st.text_input("Facebook Page Access Token:", value=default_fb_token, help="Page access token with pages_manage_posts", type="password")
    fb_link = st.text_input("Link to share on Page (optional):", value="")
    if st.button("📤 Post to Facebook Page (create post + comment)"):
        if not fb_page_id or not fb_page_token:
            st.warning("Please provide FB_PAGE_ID and FB_PAGE_TOKEN (or set them in environment variables).")
        else:
            st.info("Creating Page post and adding comment...")
            try:
                from commenter_poster import create_page_post_and_comment, generate_comment_for_url
                topics = [t.strip() for t in st.session_state.get('keyword','').split(',')] if st.session_state.get('keyword') else []
                # Generate a personalized comment first so we can include it in the post body
                gen_ok, gen_out = generate_comment_for_url(fb_link or "", topics)
                comment_to_use = gen_out if gen_ok else None

                success, details = create_page_post_and_comment(
                    fb_page_id,
                    fb_page_token,
                    fb_link or "",
                    topics,
                    excerpt=None,
                    comment_text=comment_to_use,
                    include_comment_in_post=True,
                    post_as_comment=False,  # do NOT post as a separate comment
                )
                if success:
                    st.success("Facebook post + comment created: " + details)
                else:
                    st.error("Failed: " + details)
            except Exception as e:
                st.error(f"Error while posting to Facebook: {e}")
    
    st.info("💡 Tip: Use 'Copy Comment' to copy the generated comment. To publish, use the Facebook Page flow above or your own publishing workflow.")
    
    with tab2:
        st.markdown("### 📈 Sentiment Analysis Insights")
        
        sentiment_text = st.session_state.sentiment_text if st.session_state.sentiment_text else result_text
        
        sentiment = "Neutral 😐"
        if any(word in sentiment_text.lower() for word in ["positive", "optimistic", "great", "excellent", "beneficial", "predominantly positive", "overwhelmingly positive"]):
            sentiment = "Positive 😊"
        elif any(word in sentiment_text.lower() for word in ["negative", "concerning", "worried", "critical", "predominantly negative"]):
            sentiment = "Negative 😔"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Overall Sentiment", sentiment)
        with col2:
            st.metric("📝 Analysis Length", f"{len(sentiment_text.split())} words")
        with col3:
            st.metric("🤖 AI Agents", "6")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; margin: 1rem 0;">
            <h4 style="color: white;">Sentiment Analysis Report</h4>
            <div style="color: white; line-height: 1.8; white-space: pre-wrap;">{sentiment_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Download Sentiment Analysis",
            data=sentiment_text,
            file_name=f"sentiment_analysis_{st.session_state.keyword.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_sentiment"
        )
        # Show per-URL table with actions
        st.markdown("### 🔗 Discovered URLs & Per-URL Actions")
        urls = st.session_state.get('crawler_urls', [])
        sr = st.session_state.get('sentiment_results', [])
        if urls and sr:
            for item in sr:
                url = item.get('url')
                label = item.get('label', 'unknown')
                pol = item.get('polarity')
                excerpt = item.get('excerpt','')
                col1, col2, col3 = st.columns([6,2,2])
                with col1:
                    st.markdown(f"**{label.upper()} ({pol})** — [{url}]({url})")
                    st.write(excerpt[:300] + ("..." if len(excerpt)>300 else ""))
                with col2:
                    if st.button(f"Generate comment for this URL", key=f"gen_{url}"):
                        try:
                            CommentAgent = get_comment_agent()
                            task = Task(
                                description=(
                                    f"Write a short 1-2 sentence blog comment for the article at {url}.\n"
                                    f"Article excerpt: {excerpt[:800]}\n"
                                    f"Detected sentiment: {label} (polarity={pol})\n"
                                    "Output ONLY the comment text, 1-2 sentences."
                                ),
                                agent=CommentAgent,
                                expected_output="Short blog comment"
                            )
                            one_crew = Crew(agents=[CommentAgent], tasks=[task], verbose=False)
                            one_result = one_crew.kickoff()
                            # try to extract output
                            out = ""
                            if hasattr(one_result, 'tasks_output') and one_result.tasks_output:
                                to = one_result.tasks_output[0]
                                out = getattr(to, 'raw', None) or getattr(to, 'exported_output', None) or str(to)
                            st.success("Generated comment:")
                            st.write(out)
                            # store per-url comment
                            st.session_state.setdefault('url_comments', {})[url] = out
                        except Exception as e:
                            st.error(f"Failed to generate comment: {e}")
                with col3:
                    st.info("Posting comments to arbitrary external sites has been disabled for safety.")
        else:
            st.info('No discovered URLs to display. Run an analysis to collect links.')
    
    with tab3:
        st.markdown("### ☁️ Word Cloud Visualization")
        
        try:
            wordcloud = WordCloud(
                width=1000,
                height=500,
                background_color='white',
                colormap='viridis',
                max_words=100
            ).generate(result_text)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'Most Frequent Terms in "{st.session_state.keyword}" Analysis', fontsize=16, fontweight='bold', pad=20)
            
            st.pyplot(fig)
            plt.close()
            
            st.info("💡 Larger words appear more frequently in the analysis")
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="🖼️ Download Word Cloud",
                data=buf,
                file_name=f"wordcloud_{st.session_state.keyword.replace(' ', '_')}.png",
                mime="image/png",
                key="download_wordcloud"
            )
        except Exception as e:
            st.warning(f"⚠️ Could not generate word cloud: {str(e)}")
    
    with tab4:
        st.markdown("### 📄 Complete Analysis Report")
        
        report_display = st.session_state.get('report_text', result_text)
        
        with st.expander("📋 View Full Report", expanded=True):
            st.markdown(report_display)
        
        st.text_area("Raw Text (for copying):", report_display, height=300, key="full_report_display")
        
        st.download_button(
            label="📥 Download Full Report as TXT",
            data=report_display,
            file_name=f"analysis_{st.session_state.keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            key="download_report",
            use_container_width=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Words", len(report_display.split()))
        with col2:
            st.metric("📝 Characters", len(report_display))
        with col3:
            st.metric("📄 Lines", len(report_display.split('\n')))
    
    st.balloons()
    
    st.markdown("---")
    if st.button("🔄 Analyze Another Keyword", type="secondary", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.result_text = ""
        st.rerun()

elif analyze_button and not keyword:
    st.warning("⚠️ Please enter a keyword to analyze!")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 Powered by <strong>CrewAI</strong> + <strong>OpenRouter</strong> + <strong>Streamlit</strong></p>
    <p style='font-size: 0.9rem;'>AI-Generated Blog Comments | Multi-Agent Analysis System</p>
</div>
""", unsafe_allow_html=True)
