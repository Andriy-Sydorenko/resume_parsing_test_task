import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import Select
from scraping.locators import work_ua_locators
from dotenv import load_dotenv

load_dotenv()


class BaseResumeScraper:
    """
    Base class for resume scrappers
    """
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.driver = self.init_driver()

    @staticmethod
    def init_driver():
        """
        Driver initialization method, currently uses only Edge browser
        """
        edge_options = EdgeOptions()
        # enable headless mode
        edge_options.add_argument("--headless")

        # add Edge service for better compatibility
        service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service)

        return driver

    def fetch_html(self, url: str) -> str | None:
        """
        Method to get html code of the page
        """
        try:
            self.driver.get(url=url)
            return self.driver.page_source
        except WebDriverException as error:
            print(f"An error occurred while trying to fetch the HTML from {url}: {error}")
            return None

    def parse_resumes(self):
        raise NotImplementedError

    def search_resumes(self):
        raise NotImplementedError

    def close_driver(self):
        if self.driver:
            self.driver.quit()


class WorkUaScraper(BaseResumeScraper):
    """
    Resume scrapper for work.ua
    """
    def __init__(self):
        super().__init__(os.getenv("WORK_UA_BASE_URL"))
        self.work_experience = {
            "Without experience": 0,
            "Up to 1 year": 1,
            "1-2 years": 164,
            "2-5 years": 165,
            "5+ years": 166,
        }
        self.employment_type = {
            "Full time": 74,
            "Part time": 75,
        }
        self.salaries = {
            2000: 2,
            3000: 3,
            4000: 4,
            5000: 5,
            6000: 6,
            7000: 7,
            8000: 8,
            9000: 9,
            10000: 10,
            15000: 11,
            20000: 12,
            25000: 13,
            30000: 14,
            40000: 15,
            50000: 16,
            100000: 17,
        }

    def find_resumes_without_filters(self, filters: dict):
        """
        Method that takes different filters, such as job position, location, experience,
        and applies it for search
        """
        self.fetch_html(self.base_url)

        job_position = filters.get("job_position")
        if job_position:
            job_title_field = self.driver.find_element(*work_ua_locators.JOB_TITLE_INPUT_FIELD)
            job_title_field.send_keys(job_position)

        location = filters.get("location")
        if location:
            location_field = self.driver.find_element(*work_ua_locators.LOCATION_INPUT_FIELD)
            self.driver.execute_script("arguments[0].value = '';", location_field)
            location_field.send_keys(location)
        self.find_and_click_element(work_ua_locators.SUBMIT_BUTTON)
        # suggestions_list = WebDriverWait(self.driver, 10).until(
        #     EC.visibility_of_element_located((By.CSS_SELECTOR, ".list-tips[style*='display: block;']"))
        # )
        # suggestions = suggestions_list.find_elements(By.CSS_SELECTOR, "li[role='option']")
        # if suggestions:
        #     suggestions[0].click()

    def parse_resumes(self):
        try:
            location = self.driver.find_element(*work_ua_locators.LOCATION_INPUT_FIELD)
            resume_cards = self.driver.find_elements(*work_ua_locators.RESUME_CARD)
            resumes = {"resume_cards": resume_cards}
            if location.get_property("value") in ["Вся Україна", "All Ukraine", "Вся Украина", ]:
                resumes.update({"warning": "Search is carried out throughout Ukraine, if you wanted to search for resumes in a specific city, check if you spelled ones name correctly"})

            return resumes

        except TimeoutException:
            return "Can't find any resumes with this search"
        # TODO: add check if there are not any resumes from the search

    def apply_filters(self, filters: dict):
        # wait for the list of filters to appear
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(work_ua_locators.FILTERS_BLOCK)
        )
        work_experience = filters.get("work_experience")
        employment_type = filters.get("employment_type")
        salary_from = filters.get("salary_from")
        salary_to = filters.get("salary_to")
        print(f"{salary_from = }")
        print(f"{salary_to = }")

        # apply filters if they are set
        if work_experience:
            self.find_and_click_checkbox('work_experience', work_experience,
                                       "div#experience_selection input[type='checkbox'][value='{value}']")
        if employment_type:
            self.find_and_click_checkbox('employment_type', employment_type,
                                       "div#employment_selection input[type='checkbox'][value='{value}']")
        if salary_from:
            self.find_option_in_selector_and_choose(locator=(By.ID, "salaryfrom_selection"), value=salary_from)
        if salary_to:
            self.find_option_in_selector_and_choose(locator=(By.ID, "salaryto_selection"), value=salary_to)

    def find_and_click_checkbox(self, option_type, option_value, selector_template):
        if option_value:
            value = getattr(self, option_type).get(option_value)
            css_selector = selector_template.format(value=value)
            self.find_and_click_element((By.CSS_SELECTOR, css_selector))
            time.sleep(0.5)

    def find_option_in_selector_and_choose(self, locator, value):
        try:
            select = Select(self.driver.find_element(*locator))
            select.select_by_value(str(self.salaries.get(value)))
        except NoSuchElementException:
            pass
        time.sleep(0.5)

    def find_and_click_element(self, locator: tuple[str, str]):
        element = self.driver.find_element(*locator)
        if element.is_enabled():
            element.click()


class RobotaUaScraper(BaseResumeScraper):
    """
    Resume scrapper for robota.ua
    """
    def __init__(self):
        super().__init__(os.getenv("ROBOTA_UA_BASE_URL"))
        self.categories = {}

    def parse_resumes(self):
        # TODO: implement method
        pass

    def search_resumes(self):
        # TODO: implement method
        pass
