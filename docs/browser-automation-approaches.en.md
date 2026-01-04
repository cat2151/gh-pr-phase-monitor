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

### Recommendation: Selenium WebDriver (Approach 1)

Reasons:
1. **Stability**: Industry standard with years of proven reliability
2. **Windows Support**: Can use Edge (standard Windows browser)
3. **Element Detection**: Reliable detection and clicking of HTML elements
4. **Maintainability**: Rich documentation and sample code
5. **Integration**: Easy to extend current `assign_issue_to_copilot()` function

### Implementation Steps

1. **Add Dependencies**:
   ```
   selenium>=4.0.0
   webdriver-manager>=4.0.0
   ```

2. **Add Configuration Options** (config.toml):
   ```toml
   [assign_to_copilot]
   enabled = false
   automated = false  # New: Enable automated button clicking
   wait_seconds = 10  # New: Wait time before clicking
   browser = "edge"   # New: Browser to use (edge, chrome, firefox)
   ```

3. **Extend issue_fetcher.py**:
   - Extend `assign_issue_to_copilot()` function
   - Use Selenium when `automated` setting is true
   - Use current `webbrowser.open()` when false

4. **Error Handling**:
   - Fallback to manual method if Selenium is unavailable
   - Check login state
   - Handle cases when buttons are not found

### Alternative: Playwright (Approach 2)

If you prefer a modern approach, Playwright is also a good option.
It's faster and more stable, but has fewer adoption examples.

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
2. 🔄 Implement prototype using Selenium WebDriver
3. 🔄 Add configuration options
4. 🔄 Integrate with existing code
5. 🔄 Testing and documentation updates
