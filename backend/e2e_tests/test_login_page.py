# from pages.login_page import LoginPage
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# def test_user_can_log_in(driver, flask_server, base_url):
#     page = LoginPage(driver, base_url)
#     page.load()
#     page.login("seleniumtest@gmail.com", "test_pass")
#     print(driver.current_url)
#     flag = False
#     try:
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "//h1[text()='MAFES Equipment Management System']")
#             )
#         )
#         flag = True
#     except TimeoutException:
#         flag = False
#     assert flag
