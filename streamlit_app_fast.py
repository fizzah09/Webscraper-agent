from crewai import Crew, Task
from crawleragent import CrawlerAgent
from cleaneragent import CleanerAgent
from analyzer_agent import AnalyzerAgent
from sentiment_agent import SentimentAgent
from reporter_agent import ReporterAgent
from comment_agent import CommentAgent
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import streamlit as st
import os
import warnings
import re
warnings.filterwarnings("ignore")
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
st.set_page_config(
    page_title="CrewAI Blog Analyzer & Commenter",
    page_icon="🤖",
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
st.markdown('<div class="main-header">🤖 CrewAI Blog Analyzer & Comment Generator</div>', unsafe_allow_html=True)
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

analyze_button = st.button("🚀 Start Analysis & Generate Comment", type="primary", use_container_width=True)

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
        status_text.info("🤖 Initializing AI agents...")
        
        tasks = []
        
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
        
        report_task = Task(
            description=f"Create a comprehensive analysis report about '{keyword}' combining all findings.",
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
        
        # Create and execute crew
        status_text.info("Running multi-agent analysis...")
        
        crew = Crew(
            agents=[CrawlerAgent, CleanerAgent, AnalyzerAgent, SentimentAgent, ReporterAgent, CommentAgent],
            tasks=tasks,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Mark all agents as complete
        for i in range(6):
            agent_names = ["🕷️ Crawler", "🧹 Cleaner", "🔍 Analyzer", "😊 Sentiment", "📝 Reporter", "💬 Commenter"]
            agent_containers[i].markdown(
                f'<div class="agent-box"><b>{agent_names[i]} Agent:</b> ✅ Completed</div>',
                unsafe_allow_html=True
            )
        
        progress_bar.progress(1.0)
        status_text.success("✅ Analysis Complete!")
        
        # Extract individual task outputs from CrewAI result
        # The result object contains task_output for each task
        def get_task_output(task_index):
            try:
                # Try to get from result's tasks_output list
                if hasattr(result, 'tasks_output') and len(result.tasks_output) > task_index:
                    task_out = result.tasks_output[task_index]
                    if hasattr(task_out, 'raw'):
                        return str(task_out.raw)
                    elif hasattr(task_out, 'exported_output'):
                        return str(task_out.exported_output)
                    else:
                        return str(task_out)
                # Fallback to tasks list
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
        
        # Store in session state with individual outputs
        full_result = str(result)
        st.session_state.result_text = full_result
        st.session_state.crawler_text = crawler_output
        st.session_state.cleaner_text = cleaner_output
        st.session_state.analyzer_text = analyzer_output
        st.session_state.sentiment_text = sentiment_output
        st.session_state.report_text = report_output  # ReporterAgent output
        st.session_state.comment_text = comment_output  # CommentAgent output
        st.session_state.analysis_complete = True
        
        # Force rerun to show results
        st.rerun()
        
    except Exception as e:
        status_text.error(f"❌ Error: {str(e)}")
        st.error("**Troubleshooting:**\n- Verify .env has OPENROUTER_API_KEY\n- Check conda environment is activated\n- Ensure internet connection")

# Display results if analysis was completed
elif st.session_state.analysis_complete:
    st.markdown("---")
    st.markdown(f"### 📊 Analysis Results for: **{st.session_state.keyword}**")
    
    result_text = st.session_state.result_text
    
    # Display results in tabs
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Generated Comment", "📈 Insights", "☁️ Word Cloud", "📄 Full Report"])
    
    with tab1:
        st.markdown("### 💬 AI-Generated Comment")
        
        # Use the dedicated comment text from session state
        generated_comment = st.session_state.get('comment_text', "")
        
        # Clean up the comment
        if generated_comment:
            # Remove any "Final Answer:" prefix
            generated_comment = re.sub(r'^(Comment:|Answer:|Final Answer:)\s*', '', generated_comment, flags=re.IGNORECASE)
            # Take only first 2-3 sentences
            sentences = re.split(r'[.!?]+', generated_comment)
            clean_sentences = []
            for sent in sentences[:3]:
                cleaned = sent.strip()
                if cleaned and len(cleaned) > 15:
                    clean_sentences.append(cleaned)
            if clean_sentences:
                generated_comment = '. '.join(clean_sentences) + '.'
        
        # Fallback: Generate based on sentiment if extraction failed
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
            blog_url = st.text_input("📝 Blog URL (optional):", key="blog_url", placeholder="https://example.com/blog")
        
        st.info("💡 **How to use:** Click 'Copy Comment' to download, then paste on the blog post!")
    
    with tab2:
        st.markdown("### 📈 Sentiment Analysis Insights")
        
        # Display the sentiment analysis from SentimentAgent
        sentiment_text = st.session_state.sentiment_text if st.session_state.sentiment_text else result_text
        
        # Determine sentiment for metrics
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
            <h4 style="color: white;">� Sentiment Analysis Report</h4>
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
    
    with tab3:
        st.markdown("### ☁️ Word Cloud Visualization")
        
        try:
            # Generate word cloud
            wordcloud = WordCloud(
                width=1000,
                height=500,
                background_color='white',
                colormap='viridis',
                max_words=100
            ).generate(result_text)
            
            # Display
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'Most Frequent Terms in "{st.session_state.keyword}" Analysis', fontsize=16, fontweight='bold', pad=20)
            
            st.pyplot(fig)
            plt.close()
            
            st.info("💡 Larger words appear more frequently in the analysis")
            
            # Download word cloud
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
        
        # Use the dedicated report text (not the comment!)
        report_display = st.session_state.get('report_text', result_text)
        
        # Display report in an expandable section with better formatting
        with st.expander("📋 View Full Report", expanded=True):
            st.markdown(report_display)
        
        # Also show in text area for easy copying
        st.text_area("Raw Text (for copying):", report_display, height=300, key="full_report_display")
        
        # Download button
        st.download_button(
            label="📥 Download Full Report as TXT",
            data=report_display,
            file_name=f"analysis_{st.session_state.keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            key="download_report",
            use_container_width=True
        )
        
        # Show report stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Words", len(report_display.split()))
        with col2:
            st.metric("📝 Characters", len(report_display))
        with col3:
            st.metric("📄 Lines", len(report_display.split('\n')))
    
    st.balloons()
    
    # Add button to start new analysis
    st.markdown("---")
    if st.button("🔄 Analyze Another Keyword", type="secondary", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.result_text = ""
        st.rerun()

elif analyze_button and not keyword:
    st.warning("⚠️ Please enter a keyword to analyze!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>made by students of SIR HAMMAD</p>
    <p>🤖 Powered by <strong>CrewAI</strong> + <strong>OpenRouter</strong> + <strong>Streamlit</strong></p>
    <p style='font-size: 0.9rem;'>AI-Generated Blog Comments | Multi-Agent Analysis System</p>
</div>
""", unsafe_allow_html=True)
