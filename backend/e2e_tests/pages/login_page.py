from selenium.webdriver.common.by import By

class LoginPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.url = f"{base_url}/login"

        # Locators
        self.email_input = (By.ID, "email")
        self.password_input = (By.ID, "password")
        self.submit_button = (By.CSS_SELECTOR, "button[type='submit']")

    def load(self):
        self.driver.get(self.url)

    def login(self, email, password):
        self.driver.find_element(*self.email_input).send_keys(email)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.submit_button).click()
