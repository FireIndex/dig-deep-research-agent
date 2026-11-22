import logging
import time

from log_config import setup_logging
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

setup_logging()
logger = logging.getLogger(__name__)

STAGE_NAMES = ["search", "reader", "writer", "critic"]


def run_research_pipeline(topic : str, on_stage=None) -> dict:
    """on_stage(index, "start" | "done") is optional - lets a UI follow progress."""
    stage_t0 = {}

    def emit(i, status):
        if status == "start":
            stage_t0[i] = time.time()
            logger.info("Stage %s started", STAGE_NAMES[i])
        else:
            logger.info("Stage %s done in %.1fs", STAGE_NAMES[i], time.time() - stage_t0.get(i, time.time()))
        if on_stage:
            on_stage(i, status)

    logger.info("Pipeline started, topic=%r", topic)
    pipeline_t0 = time.time()
    try:
        state = _run(topic, emit)
    except Exception:
        logger.exception("Pipeline failed after %.1fs, topic=%r", time.time() - pipeline_t0, topic)
        raise
    logger.info("Pipeline finished in %.1fs", time.time() - pipeline_t0)
    return state


def _run(topic: str, emit) -> dict:
    state = {}

    #search agent working
    # print("\n"+" ="*50)
    # print("step 1 - search agent is working ...")
    # print("="*50)

    emit(0, "start")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content
    # print("\n search result ", state['search_results'])
    emit(0, "done")

    #step 2 - reader agent
    # print("\n"+" ="*50)
    # print("step 2 - Reader agent is scraping top resources ...")
    # print("="*50)

    emit(1, "start")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    # print("\nscraped content: \n", state['scraped_content'])
    emit(1, "done")

    #step 3 - writer chain

    # print("\n"+" ="*50)
    # print("step 3 - Writer is drafting the report ...")
    # print("="*50)

    emit(2, "start")
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    # print("\n Final Report\n",state['report'])
    emit(2, "done")

    #critic report

    # print("\n"+" ="*50)
    # print("step 4 - critic is reviewing the report ")
    # print("="*50)

    emit(3, "start")
    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    # print("\n critic report \n", state['feedback'])
    emit(3, "done")

    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    print(run_research_pipeline(topic))
