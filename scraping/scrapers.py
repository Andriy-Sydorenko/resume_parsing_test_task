import asyncio
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from scraping.locators import work_ua_locators

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
        edge_options.add_argument("--headless")  # Enable headless mode
        edge_options.add_argument("--disable-gpu")  # Sometimes required for headless mode

        # Add Edge service for better compatibility
        service = EdgeService(executable_path=EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)

        return driver

    async def fetch_html(self, url: str) -> str | None:
        """
        Method to get html code of the page
        """
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, lambda: self.driver.get(url=url))
            return self.driver.page_source
        except WebDriverException as error:
            print(f"An error occurred while trying to fetch the HTML from {url}: {error}")
            return None

    def parse_resumes(self):
        raise NotImplementedError

    def search_resumes(self):
        raise NotImplementedError

    async def close_driver(self):
        if self.driver:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.driver.quit)

    @staticmethod
    async def find_element_async(driver, locator, loop) -> WebElement:
        return await loop.run_in_executor(None, lambda: driver.find_element(*locator))

    @staticmethod
    async def find_elements_async(driver, locator, loop) -> list[WebElement]:
        return await loop.run_in_executor(None, lambda: driver.find_elements(*locator))

    @staticmethod
    async def send_keys_async(driver, keys, loop) -> None:
        await loop.run_in_executor(None, lambda: driver.send_keys(keys))


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

    async def find_resumes_without_filters(self, filters: dict):
        """
        Method that takes different filters, such as job position, location, experience,
        and applies it for search
        """
        await self.fetch_html(self.base_url)
        loop = asyncio.get_running_loop()

        job_position = filters.get("job_position")
        if job_position:
            job_title_field = await self.find_element_async(self.driver,
                                                            work_ua_locators.JOB_TITLE_INPUT_FIELD,
                                                            loop)
            await self.send_keys_async(job_title_field, job_position, loop)

        location = filters.get("location")
        if location:
            location_field = await self.find_element_async(self.driver,
                                                           work_ua_locators.LOCATION_INPUT_FIELD,
                                                           loop)
            self.driver.execute_script("arguments[0].value = '';", location_field)
            await self.send_keys_async(location_field, location, loop)
        await self.find_and_click_element(work_ua_locators.SUBMIT_BUTTON)

    async def parse_resumes(self):
        try:
            loop = asyncio.get_running_loop()
            # checking for pagination
            pagination = await self.find_elements_async(self.driver, work_ua_locators.RESUME_PAGINATION, loop)
            total_pages = 1

            if pagination:
                # if pagination exists, we need to find total number of pages
                page_numbers = await self.find_elements_async(pagination[0], (By.CSS_SELECTOR, "li a"), loop)
                if page_numbers:
                    total_pages = int(page_numbers[-2].text)

            current_page = self.driver.current_url
            all_resume_cards = []
            for page in range(1, total_pages + 1):
                if page > 1:
                    page_query_parameter = f"page={page}"
                    next_page_url = (f"{current_page}&{page_query_parameter}"
                                     if "?" in current_page
                                     else f"{current_page}?{page_query_parameter}")
                    await self.fetch_html(next_page_url)

                resume_cards = await self.find_elements_async(self.driver, work_ua_locators.RESUME_CARD, loop)
                users_data = []
                for resume in resume_cards:
                    link = await self.find_element_async(resume, (By.CSS_SELECTOR, "h2.cut-top a"), loop)
                    candidate_name = await self.find_element_async(resume,
                                                                   (By.CSS_SELECTOR,
                                                                    "p.add-top-xs.cut-bottom > span.strong-600"),
                                                                   loop)
                    users_data.append({
                        link.get_attribute("href"): {
                            "candidate_occupation": link.text,
                            "candidate_name": candidate_name.text,
                        }
                    })
                all_resume_cards.extend(users_data)
            location = await self.find_element_async(self.driver, work_ua_locators.LOCATION_INPUT_FIELD, loop)
            resumes = {"resume_cards": all_resume_cards, "total_resumes": len(all_resume_cards)}

            if location.get_property("value") in ["Вся Україна", "All Ukraine", "Вся Украина", ]:
                resumes.update({"city_error_warning": ("Search is carried out throughout Ukraine, "
                                                       "if you wanted to search for resumes in a specific city, "
                                                       "check if you spelled ones name correctly")})
            return resumes

        except TimeoutException:
            return "Can't find any resumes with this search"
        # TODO: add check if there are not any resumes from the search

    async def apply_filters(self, filters: dict):
        # wait for the list of filters to appear
        url_with_filters = self.driver.current_url + "?"
        work_experience = filters.get("work_experience")
        employment_type = filters.get("employment_type")
        salary_from = filters.get("salary_from")
        salary_to = filters.get("salary_to")
        # apply filters if they are set
        if work_experience:
            url_with_filters += f"&experience={self.work_experience.get(work_experience)}"
        if employment_type:
            url_with_filters += f"&employment={self.employment_type.get(employment_type)}"
        if salary_from:
            url_with_filters += f"&salaryfrom={self.salaries.get(salary_from)}"
        if salary_to:
            url_with_filters += f"&salaryto={self.salaries.get(salary_to)}"
        self.driver.get(url=url_with_filters)

    async def find_and_click_checkbox(self, option_type, option_value, selector_template):
        if option_value:
            value = getattr(self, option_type).get(option_value)
            css_selector = selector_template.format(value=value)
            await self.find_and_click_element((By.CSS_SELECTOR, css_selector))
            time.sleep(0.5)

    # async def find_option_in_selector_and_choose(self, locator, value):
    #     try:
    #         select = Select(self.driver.find_element(*locator))
    #         select.select_by_value(str(self.salaries.get(value)))
    #     except NoSuchElementException:
    #         pass
    #     time.sleep(0.5)

    async def find_and_click_element(self, locator: tuple[str, str]):
        loop = asyncio.get_running_loop()
        element = await self.find_element_async(self.driver, locator, loop)
        if element.is_enabled():
            await loop.run_in_executor(None, element.click)


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
