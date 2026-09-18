*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    Process

*** Variables ***
${BUILD_PATH}    ${EMPTY}
${PLATFORM_URL}    http://localhost:3000

*** Test Cases ***
Advanced Build Workflows
    [Documentation]    Test advanced build creation and management
    ${start}=    Get Time    epoch
    Open Browser    ${PLATFORM_URL}    chrome
    Maximize Browser Window
    
    # Login as power user
    Input Text    id=email    poweruser@platform.com
    Input Text    id=password    PowerUser123!
    Click Element    id=login-btn
    Wait Until Page Contains    Dashboard    10s
    
    # Create multiple builds
    FOR    ${i}    IN RANGE    1    4
        Click Element    xpath=//button[contains(text(),"Create New Build")]
        Wait Until Page Contains Element    id=build-name    5s
        Input Text    id=build-name    Advanced Build ${i}
        Select From List By Value    id=build-type    ${i % 2 == 0 and "mobile-app" or "web-app"}
        Click Element    id=create-build-btn
        Wait Until Page Contains    Build created successfully    10s
        Sleep    1s
    END
    
    # Test build collaboration
    Click Element    xpath=//div[contains(@class,"build-card")][1]
    Wait Until Page Contains Element    id=invite-collaborator-btn    5s
    Click Element    id=invite-collaborator-btn
    Input Text    id=collaborator-email    collaborator@platform.com
    Click Element    id=send-invite-btn
    Wait Until Page Contains    Invitation sent    10s
    
    # Test build versioning
    Click Element    id=create-version-btn
    Input Text    id=version-name    v2.0.0
    Input Text    id=version-notes    Major feature update
    Click Element    id=save-version-btn
    Wait Until Page Contains    Version created    10s
    
    Close Browser
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Advanced workflows test took ${duration} seconds

Content Engine Advanced Features
    [Documentation]    Test advanced content creation features
    ${start}=    Get Time    epoch
    Open Browser    ${PLATFORM_URL}    chrome
    Maximize Browser Window
    
    # Login and access content engine
    Input Text    id=email    poweruser@platform.com
    Input Text    id=password    PowerUser123!
    Click Element    id=login-btn
    Wait Until Page Contains    Dashboard    10s
    
    Click Element    xpath=//a[contains(text(),"Content Creation")]
    Wait Until Page Contains    Hood Alchemy Content Engine    15s
    
    # Test batch episode creation
    Click Element    xpath=//button[contains(text(),"Batch Create")]
    Wait Until Page Contains Element    id=batch-count    5s
    Input Text    id=batch-count    3
    Click Element    id=batch-upload-btn
    # Would need multiple MP3 files for full test
    Wait Until Page Contains    Batch setup complete    30s
    
    # Test custom DNA configuration
    Click Element    xpath=//button[contains(text(),"Custom DNA")]
    Wait Until Page Contains Element    id=dna-editor    5s
    Input Text    id=dna-editor    {"comedy_modules": ["custom_module_1"]}
    Click Element    id=save-dna-btn
    Wait Until Page Contains    DNA configuration saved    10s
    
    # Test marketing campaign creation
    Click Element    xpath=//button[contains(text(),"Marketing Campaign")]
    Wait Until Page Contains Element    id=campaign-name    5s
    Input Text    id=campaign-name    Power User Campaign
    Select From List By Value    id=campaign-type    social-media
    Click Element    id=create-campaign-btn
    Wait Until Page Contains    Campaign created    15s
    
    Close Browser
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Advanced content test took ${duration} seconds

Performance Under Load
    [Documentation]    Test platform performance with multiple concurrent operations
    ${start}=    Get Time    epoch
    
    # Test multiple browser sessions
    FOR    ${i}    IN RANGE    1    6
        Open Browser    ${PLATFORM_URL}    chrome    alias=session_${i}
        Maximize Browser Window
        Go To    ${PLATFORM_URL}
        Input Text    id=email    user${i}@platform.com
        Input Text    id=password    TestPass123!
        Click Element    id=login-btn
        Wait Until Page Contains    Dashboard    15s
    END
    
    # Test concurrent build operations
    Switch Browser    session_1
    FOR    ${i}    IN RANGE    1    4
        Click Element    xpath=//button[contains(text(),"Create New Build")]
        Input Text    id=build-name    Load Test Build ${i}
        Click Element    id=create-build-btn
        Wait Until Page Contains    Build created successfully    20s
    END
    
    # Close all browsers
    FOR    ${i}    IN RANGE    1    6
        Close Browser
    END
    
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Load test took ${duration} seconds

Cheetah V3 Advanced Usage
    [Documentation]    Test advanced Cheetah V3 autocoder features
    ${start}=    Get Time    epoch
    
    # Test multiple task generation
    ${result}=    Run Process    cd ../../../Site Features/Overlay-Cheetah-V3-main && python3 autocoder.py --once    shell=True
    Should Be Equal As Integers    ${result.rc}    0
    
    # Test template validation
    ${result}=    Run Process    cd ../../../Site Features/Overlay-Cheetah-V3-main && find templates -name "*.j2" | wc -l    shell=True
    Should Be True    int(${result.stdout.strip()}) > 10
    
    # Test output generation
    ${result}=    Run Process    cd ../../../Site Features/Overlay-Cheetah-V3-main && ls -la out/ | wc -l    shell=True
    Should Be True    int(${result.stdout.strip()}) > 5
    
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Advanced Cheetah test took ${duration} seconds

*** Keywords ***
Start Application
    [Arguments]    ${path}
    Log    Starting application: ${path}
    Run Process    ${path}    shell=True

Close Application
    Log    Closing application
    Terminate All Processes
