from pathlib import Path
import time
import pytest
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BaseCase.main(__name__, __file__)

# Set the paths to the images and csv file
repo_path = Path(__file__).resolve().parents[2]
imgpath = repo_path / "tests/data/rand_images"
img_f1 = imgpath / "img_001.jpg"
img_f2 = imgpath / "img_002.jpg"
img_f3 = imgpath / "img_003.jpg"
#csvpath = repo_path / "tests/data/test_csvs"
#csv_f1 = csvpath / "debian.csv"

mk_visible = """
            var input = document.querySelector('[data-testid="stFileUploaderDropzoneInput"]');
            input.style.display = 'block';
            input.style.opacity = '1';
            input.style.visibility = 'visible';
            """

def wait_for_element(self, by, selector, timeout=10):
    # example usage:
    # element = self.wait_for_element(By.XPATH, "//p[contains(text(), 'Species for observation')]")
    
    return WebDriverWait(self.driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def find_all_button_paths(self):
    buttons = self.find_elements("button")
    for button in buttons:
        print(f"\nButton found:")
        print(f"Text: {button.text.strip()}")
        print(f"HTML: {button.get_attribute('outerHTML')}")
        print("-" * 50)

def check_columns_and_images(self, exp_cols:int, exp_imgs:int=4):
    # Find all columns
    columns = self.find_elements("div[class*='stColumn']")
    
    # Check number of columns 
    assert len(columns) == exp_cols, f"Expected exp_cols columns but found {len(columns)}"
    
    # Check images in each column
    for i, column in enumerate(columns, 1):
        # Find all images within this column's image containers
        images = self.find_elements(
            f"div[class*='stColumn']:nth-child({i}) div[data-testid='stImageContainer'] img"
        )
        
        # Check number of images in this column 
        assert len(images) == exp_imgs, f"Column {i} has {len(images)} images instead of {exp_imgs}"


def analyze_species_columns_debug(self):
    # First, just try to find any divs
    all_divs = self.find_elements(By.TAG_NAME, "div")
    print(f"Found {len(all_divs)} total divs")

    # Then try to find stColumn divs
    column_divs = self.find_elements(By.XPATH, "//div[contains(@class, 'stColumn')]")
    print(f"Found {len(column_divs)} column divs")

    # Try to find any elements containing our text, without class restrictions
    text_elements = self.find_elements(
        By.XPATH, "//*[contains(text(), 'Species for observation')]"
    )
    print(f"Found {len(text_elements)} elements with 'Species for observation' text")

    # If we found text elements, print their tag names and class names to help debug
    for elem in text_elements:
        print(f"Tag: {elem.tag_name}, Class: {elem.get_attribute('class')}")

def analyze_species_columns(self, exp_cols:int, exp_imgs:int=4, exp_visible:bool=True):
    # Find all columns that contain the specific text pattern
    cur_tab = get_selected_tab(self)
    print(f"Current tab: {cur_tab['text']} ({cur_tab['id']})" )
    
    #"div[class*='stColumn']//div[contains(text(), 'Species for observation')]"
    spec_labels = self.find_elements(
        By.XPATH, 
        "//p[contains(text(), 'Species for observation')]"
    )
    
    # This gets us the text containers, need to go back up to the column
    species_columns = [lbl.find_element(By.XPATH, "./ancestor::div[contains(@class, 'stColumn')]") 
                      for lbl in spec_labels]
     
    print(f"   Found {len(species_columns)} species columns (total {len(spec_labels)} species labels)")
    assert len(species_columns) == exp_cols, f"Expected {exp_cols} columns but found {len(species_columns)}"
    
    
    for i, column in enumerate(species_columns, 1):
        # Get the species number text
        species_text = column.find_element(
            #By.XPATH, ".//div[contains(text(), 'Species for observation')]"
            By.XPATH, ".//p[contains(text(), 'Species for observation')]"
        )
        print(f"   Analyzing col {i}:{species_text.text} {species_text.get_attribute('outerHTML')} | ")
        
        # Find images in this specific column
        images = column.find_elements(
            By.XPATH, ".//div[@data-testid='stImageContainer']//img"
        )
        print(f"   - Contains {len(images)} images (expected: {exp_imgs})")
        assert len(images) == exp_imgs, f"Column {i} has {len(images)} images instead of {exp_imgs}"

        # now let's refine the search to find the images that are actually displayed
        visible_images = [img for img in column.find_elements(
            By.XPATH, ".//div[@data-testid='stImageContainer']//img"
        ) if img.is_displayed()]
        print(f"   - Contains {len(visible_images)} visible images")
        if exp_visible:
            assert len(visible_images) == exp_imgs, f"Column {i} has {len(visible_images)} visible images instead of {exp_imgs}"
        else:
            assert len(visible_images) == 0, f"Column {i} has {len(visible_images)} visible images instead of 0"
            

        # even more strict test for visibility
        # for img in images:
        #     style = img.get_attribute('style')
        #     computed_style = self.driver.execute_script(
        #         "return window.getComputedStyle(arguments[0])", img
        #     )
        #     print(f"Style: {style}")
        #     print(f"Visibility: {computed_style['visibility']}")
        #     print(f"Opacity: {computed_style['opacity']}")

def get_selected_tab(self):
    selected_tab = self.find_element(
        By.XPATH, "//div[@data-testid='stTabs']//button[@aria-selected='true']"
    )
    # Get the tab text
    tab_text = selected_tab.find_element(By.TAG_NAME, "p").text
    # Get the tab index (might be useful)
    tab_id = selected_tab.get_attribute("id")  # Usually ends with "-tab-X" where X is the index
    return {
        "text": tab_text,
        "id": tab_id,
        "element": selected_tab
    }

def switch_tab(self, tab_number):
    # Click the tab
    self.click(f"div[data-testid='stTabs'] button[id$='-tab-{tab_number}'] p")
    
    # Verify the switch
    selected_tab = get_selected_tab(self)
    if selected_tab["id"].endswith(f"-tab-{tab_number}"):
        print(f"Successfully switched to tab {tab_number}: {selected_tab['text']}")
    else:
        raise Exception(f"Failed to switch to tab {tab_number}, current tab is {selected_tab['text']}")

class RecorderTest(BaseCase):

    @pytest.mark.slow
    @pytest.mark.visual
    def test_species_presentation(self):
        # this test goes through several steps of the workflow, primarily to get to the point
        # that species columns are displayed.
        # - setup steps: 
        #    - open the app
        #    - upload two images
        #    - validate the data entry
        #    - click the infer button, wait for ML
        # - the real test steps: 
        #    - check the species columns are displayed
        #    - switch to another tab, check the columns are not displayed
        #    - switch back to the first tab, check the columns are displayed again
        
        self.open("http://localhost:8501/")
        time.sleep(4) # even in demo mode, on full script this is needed 
        # (the folium maps cause the scripts to rerun, which means the wait_for_element finds it, but
        #  the reload is going on and this makes the upload files (send_keys) command fail)
        
        # make the file_uploader block visible -- for some reason even though we can see it, selenium can't...
        wait_for_element(self, By.CSS_SELECTOR, '[data-testid="stFileUploaderDropzoneInput"]')
        self.execute_script(mk_visible)
        # send a list of files
        self.send_keys(
            'input[data-testid="stFileUploaderDropzoneInput"]', 
            "\n".join([str(img_f1), str(img_f2)]),
        )
        
        # advance to the next step, by clicking the validate button (wait for it first)
        wait_for_element(self, By.XPATH, "//button//strong[contains(text(), 'Validate')]")
        self.click('button strong:contains("Validate")')
        # validate the progress via the text display
        self.assert_exact_text("Progress: 2/5. Current: data_entry_validated.", 'div[data-testid="stMarkdownContainer"] p em')
        
        # check the tab bar is there, and the titles are correct
        expected_texts = [
            "Cetecean classifier", "Hotdog classifier", "Map",
            "Dev:coordinates", "Log", "Beautiful cetaceans"
        ]
        self.assert_element("div[data-testid='stTabs']") 

        for i, text in enumerate(expected_texts):
            selector = f"div[data-testid='stTabs'] button[id$='-tab-{i}'] p"
            print(f"{i=}, {text=}, {selector=}")
            self.assert_text(text, selector)
            break # just do one, this is slow while debuggin

        # dbg: look for buttons, find out which props will isolate the right one.
        # find_all_button_paths(self)

        self.assert_element(".st-key-button_infer_ceteans button")
        self.click(".st-key-button_infer_ceteans button")
        
        # check the state has advanced
        self.assert_exact_text("Progress: 3/5. Current: ml_classification_completed.", 
                               'div[data-testid="stMarkdownContainer"] p em')

        # on the inference tab, check the columns and images are rendered correctly
        # - normally it is selected by default, but we can switch to it to be sure
        # - then we do the test for the right number of columns and images per col,
        #   which should be visible
        switch_tab(self, 0)
        analyze_species_columns(self, exp_cols=2, exp_imgs=4, exp_visible=True)

        # now, we want to select another tab, check somethign is present?
        # then go back, and re-check the columns and images are re-rendered.
        switch_tab(self, 4)
        assert get_selected_tab(self)["id"].endswith("-tab-4")

        # now we click the refresh button
        self.click('button[data-testid="stBaseButton-secondary"]')
        # and then select the first tab again
        switch_tab(self, 0)
        assert get_selected_tab(self)["id"].endswith("-tab-0")
        # and check the columns and images are re-rendered
        analyze_species_columns(self, exp_cols=2, exp_imgs=4, exp_visible=True)
        
        # now go to some other tab, and check the columns and images are not visible
        switch_tab(self, 2)
        assert get_selected_tab(self)["id"].endswith("-tab-2")
        analyze_species_columns(self, exp_cols=2, exp_imgs=4, exp_visible=False)
        
