from selenium.webdriver.common.by import By

JOB_TITLE_INPUT_FIELD = (By.CSS_SELECTOR, "div.input-search-job input")
LOCATION_INPUT_FIELD = (By.CSS_SELECTOR, "div.input-search-city input")
RESUME_CARD = (By.CSS_SELECTOR, "div.resume-link")
SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
RESUMES_NOT_FOUND = (By.CSS_SELECTOR, "p > b > span.wordwrap.text-muted")
FILTERS_BLOCK = (By.CSS_SELECTOR, "div#filter-wrapper div#filters-block")
RESUME_PAGINATION = (By.CSS_SELECTOR, "nav ul.pagination")
