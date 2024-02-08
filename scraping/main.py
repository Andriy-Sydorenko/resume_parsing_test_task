from scraping.scrapers import WorkUaScraper

RESUME_DISPLAY_COUNT = 5


async def parse_resumes(filters: dict):
    parser = WorkUaScraper()
    # TODO: make method universal, not only for work ua
    await parser.find_resumes_without_filters(filters=filters)
    await parser.apply_filters(filters=filters)
    result = await parser.parse_resumes()
    total_resume_amount = result.get("total_resumes")
    resume_cards = result.get("resume_cards")[:RESUME_DISPLAY_COUNT]  # limit resume count
    # TODO: change warning return if there will be more warnings implemented
    warning = result.get("city_error_warning")
    await parser.close_driver()

    return resume_cards, total_resume_amount, warning
