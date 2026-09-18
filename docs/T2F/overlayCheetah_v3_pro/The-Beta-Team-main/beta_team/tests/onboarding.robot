*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    Process

*** Variables ***
${BUILD_PATH}    ${EMPTY}
${PLATFORM_URL}    http://localhost:3000
${CONTENT_ENGINE_URL}    http://localhost:8000

*** Test Cases ***
Platform Core Functionality
    [Documentation]    Test core IP Builder Platform features
    ${start}=    Get Time    epoch
    Open Browser    ${PLATFORM_URL}    chrome
    Maximize Browser Window

    # Test landing page
    Wait Until Page Contains    IP Builder Platform    30s
    Page Should Contain Element    xpath=//button[contains(text(),"Get Started")]

    # Test user registration flow
    Click Element    xpath=//button[contains(text(),"Start")]
    Wait Until Page Contains Element    id=email    10s
    Input Text    id=email    beta_tester@platform.com
    Input Text    id=password    BetaTest123!
    Click Element    id=register-btn
    Wait Until Page Contains    Welcome to IP Builder    15s

    # Test build creation
    Click Element    xpath=//button[contains(text(),"Create New Build")]
    Wait Until Page Contains Element    id=build-name    10s
    Input Text    id=build-name    Beta Test Build
    Select From List By Value    id=build-type    web-app
    Click Element    id=create-build-btn
    Wait Until Page Contains    Build created successfully    15s

    Close Browser
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Platform core test took ${duration} seconds

Content Creation Engine Integration
    [Documentation]    Test Content Creation Engine integration
    ${start}=    Get Time    epoch
    Open Browser    ${PLATFORM_URL}    chrome
    Maximize Browser Window

    # Login and navigate to content tools
    Input Text    id=email    beta_tester@platform.com
    Input Text    id=password    BetaTest123!
    Click Element    id=login-btn
    Wait Until Page Contains    Dashboard    10s

    # Access Content Creation Engine
    Click Element    xpath=//a[contains(text(),"Content Creation")]
    Wait Until Page Contains    Hood Alchemy Content Engine    15s

    # Test episode creation
    Click Element    xpath=//button[contains(text(),"Create Episode")]
    Wait Until Page Contains Element    id=episode-id    10s
    Input Text    id=episode-id    beta_test_ep_001
    Click Element    id=upload-mp3-btn
    Wait Until Page Contains    Episode setup complete    20s

    Close Browser
    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Content engine test took ${duration} seconds

Cheetah V3 Integration Test
    [Documentation]    Test Overlay Cheetah V3 autocoder integration
    ${start}=    Get Time    epoch

    # Test autocoder functionality
    ${autocoder_abs_path}=    Set Variable    C:\Users\tap45\Desktop\Repo Assist\IP-Builder-Platform--main\build tools\Overlay-Cheetah-V3-main\autocoder.py
    ${result}=    Run Process    python    "${autocoder_abs_path}"    --once
    Log    rc: ${result.rc}
    Log    stdout: ${result.stdout}
    Log    stderr: ${result.stderr}
    Log Many    @{result.stdout_lines}
    Log Many    @{result.stderr_lines}
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    AutoCoder

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Cheetah V3 test took ${duration} seconds

Build Tools Integration
    [Documentation]    Test various build tools integration
    ${start}=    Get Time    epoch

    # Test Hardhat integration
    ${result}=    Run Process    cd "../../../build tools/hardhat-hardhat-3.0.16" && npm --version    shell=True
    Should Be Equal As Integers    ${result.rc}    0

    # Test Web3 decoder
    ${result}=    Run Process    cd "../../../build tools/web3-decoder-main" && ls -la    shell=True
    Should Be Equal As Integers    ${result.rc}    0

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Build tools test took ${duration} seconds

*** Keywords ***
Start Application
    [Arguments]    ${path}
    Log    Starting application: ${path}
    Run Process    ${path}    shell=True

Close Application
    Log    Closing application
    Terminate All Processes
