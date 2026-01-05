# Browser Automation Approaches for Button Clicking

## Requirements
Based on PR 65, implement the following functionality:
1. Launch a browser
2. Wait 10 seconds
3. Automatically click 2 buttons:
   - "Assign to Copilot" button
   - "Assign" button

**Target Environment**: Windows PC

## Approaches to Consider

### Approach 1: Selenium WebDriver (Recommended)

**Overview**: Industry-standard browser automation tool

**Pros**:
- ✅ Windows compatible (Chrome, Edge, Firefox, etc.)
- ✅ High stability
- ✅ Rich documentation and community support
- ✅ Easy element waiting and detection
- ✅ Can maintain GitHub login state (using existing profile)

**Cons**:
- ❌ Additional dependencies required (selenium, webdriver)
- ❌ Browser driver installation needed (ChromeDriver, EdgeDriver, etc.)

**Implementation Example**:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def assign_issue_to_copilot_automated(issue_url):
    # Use Edge (pre-installed on Windows)
    options = webdriver.EdgeOptions()
    # Use existing user profile to maintain login state
    # options.add_argument("user-data-dir=C:\\Users\\<username>\\AppData\\Local\\Microsoft\\Edge\\User Data")
    
    driver = webdriver.Edge(options=options)
    
    try:
        # Open the issue
        driver.get(issue_url)
        
        # Wait 10 seconds
        time.sleep(10)
        
        # Find and click "Assign to Copilot" button
        wait = WebDriverWait(driver, 10)
        assign_to_copilot_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Assign to Copilot')]"))
        )
        assign_to_copilot_btn.click()
        
        # Wait a bit
        time.sleep(2)
        
        # Find and click "Assign" button
        assign_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Assign')]"))
        )
        assign_btn.click()
        
        print("✓ Successfully assigned issue to Copilot")
        
        # Optionally close the browser
        time.sleep(2)
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to automate button clicks: {e}")
        driver.quit()
        return False
```

**Required Dependencies**:
```
selenium>=4.0.0
webdriver-manager  # Automatic driver management
```

### Approach 2: Playwright (Modern Alternative)

**Overview**: Modern browser automation tool by Microsoft

**Pros**:
- ✅ Windows compatible
- ✅ Faster and more stable
- ✅ Automatic browser driver management
- ✅ Modern API design
- ✅ Can use existing browser contexts

**Cons**:
- ❌ Additional dependencies required
- ❌ Newer than Selenium, fewer adoption examples

**Implementation Example**:
```python
from playwright.sync_api import sync_playwright
import time

def assign_issue_to_copilot_automated(issue_url):
    with sync_playwright() as p:
        # Launch Chromium (or chrome, edge, firefox)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Open the issue
            page.goto(issue_url)
            
            # Wait 10 seconds
            time.sleep(10)
            
            # Click "Assign to Copilot" button
            page.click("button:has-text('Assign to Copilot')")
            
            # Wait a bit
            time.sleep(2)
            
            # Click "Assign" button
            page.click("button:has-text('Assign')")
            
            print("✓ Successfully assigned issue to Copilot")
            
            time.sleep(2)
            browser.close()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to automate button clicks: {e}")
            browser.close()
            return False
```

**Required Dependencies**:
```
playwright>=1.40.0
```

After installation:
```bash
playwright install chromium
```

### Approach 3: PyAutoGUI (Screen Coordinate Based)

**Overview**: Direct control of screen coordinates and keyboard/mouse operations

**Pros**:
- ✅ Windows compatible
- ✅ Simple implementation

**Cons**:
- ❌ Depends on screen resolution and window position
- ❌ Breaks when button positions change
- ❌ Very unstable
- ❌ Not recommended

**Implementation Example** (reference only):
```python
import pyautogui
import time
import webbrowser

def assign_issue_to_copilot_automated(issue_url):
    # Open browser
    webbrowser.open(issue_url)
    
    # Wait 10 seconds
    time.sleep(10)
    
    # Find and click button on screen (not recommended)
    # Requires image recognition of button
    try:
        location = pyautogui.locateOnScreen('assign_to_copilot_button.png')
        if location:
            pyautogui.click(location)
    except:
        pass
```

### Approach 4: AutoHotkey (Windows-only)

**Overview**: Windows-specific automation scripting language

**Pros**:
- ✅ Optimized for Windows
- ✅ Good at keyboard/mouse operations

**Cons**:
- ❌ Complex Python integration
- ❌ Difficult to detect HTML elements
- ❌ Requires learning a different language

## Recommended Approach

### Implementation Status: Both Backends Supported

Both browser automation backends (Selenium and Playwright) are now implemented and can be selected via configuration.

### Selenium WebDriver (Approach 1)

**Features**:
1. **Stability**: Industry standard with years of proven reliability
2. **Windows Support**: Can use Edge (standard Windows browser)
3. **Element Detection**: Reliable detection and clicking of HTML elements
4. **Maintainability**: Rich documentation and sample code
5. **Integration**: Easy to extend current `assign_issue_to_copilot()` function

### Playwright (Approach 2)

**Features**:
1. **Speed**: Faster execution
2. **Easy Setup**: Browsers are automatically managed
3. **Modern API**: Latest API design with auto-waiting functionality
4. **Multiple Browser Engines**: Supports Chromium, Firefox, and WebKit

### Implementation Steps

1. **Add Dependencies** (one or both):
   ```
   # Selenium
   selenium>=4.0.0
   webdriver-manager>=4.0.0
   
   # Playwright
   playwright>=1.40.0
   ```

2. **Add Configuration Options** (config.toml):
   ```toml
   [assign_to_copilot]
   enabled = false
   automated = false               # Enable automated button clicking
   automation_backend = "selenium" # Backend: "selenium" or "playwright"
   wait_seconds = 10               # Wait time before clicking
   browser = "edge"                # Selenium: "edge", "chrome", "firefox"
                                   # Playwright: "chromium", "firefox", "webkit"
   headless = false                # Headless mode (no visible window)
   ```

3. **Usage**:
   - Set `automation_backend` to "selenium" or "playwright"
   - Both can be installed for comparison
   - Default is Selenium

4. **Error Handling**:
   - Fallback to manual method if backend is unavailable
   - Check login state
   - Handle cases when buttons are not found

### Comparison and Verification

With both backends implemented, you can now:

1. **Compare Performance**: Use `demo_comparison.py` script to compare both
2. **Verify Stability**: Test both in real environments
3. **Evaluate Usability**: Compare setup and maintainability

**Run Comparison Demo**:
```bash
python demo_comparison.py
```

## Important Considerations

1. **GitHub Login State**:
   - Automation requires GitHub login
   - Use user profile or configure credentials

2. **Security**:
   - Don't embed credentials in code
   - Recommended to use existing browser session

3. **GitHub Terms of Service**:
   - Ensure automation doesn't violate GitHub's ToS
   - Avoid excessive requests

4. **Maintainability**:
   - Selectors need updating if GitHub UI changes

## Next Steps

1. ✅ Research and document approaches (Complete)
2. ✅ Implement prototype using Selenium WebDriver (Complete)
3. ✅ Implement Playwright backend (Complete)
4. ✅ Add configuration options (Complete)
5. ✅ Integrate with existing code (Complete)
6. ✅ Testing and documentation updates (Complete)
7. 🔄 Test and verify in real environments
8. 🔄 Evaluate which is more suitable
