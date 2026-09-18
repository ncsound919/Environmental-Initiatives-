*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem

*** Variables ***
${TOOLS_BASE_URL}    file://${CURDIR}/../../mundane-offerings

*** Test Cases ***
Office Tools Test
    [Documentation]    Test all office utility tools
    ${start}=    Get Time    epoch

    # Test Document Merger
    Open Browser    ${TOOLS_BASE_URL}/office/document-merger/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Document Merger    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Test document content
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Expense Tracker
    Open Browser    ${TOOLS_BASE_URL}/office/expense-tracker/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Expense Tracker    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Office supplies: $50
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Meeting Scheduler
    Open Browser    ${TOOLS_BASE_URL}/office/meeting-scheduler/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Meeting Scheduler    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Team meeting at 2 PM
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Task Manager
    Open Browser    ${TOOLS_BASE_URL}/office/task-manager/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Task Manager    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Complete project report
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Office tools test took ${duration} seconds

Biotech Tools Test
    [Documentation]    Test all biotech utility tools
    ${start}=    Get Time    epoch

    # Test DNA Analyzer
    Open Browser    ${TOOLS_BASE_URL}/biotech/dna-analyzer/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    DNA Sequence Analyzer    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    ATCGATCG
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Lab Notebook
    Open Browser    ${TOOLS_BASE_URL}/biotech/lab-notebook/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Digital Lab Notebook    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Experiment notes
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Data Visualizer
    Open Browser    ${TOOLS_BASE_URL}/biotech/data-visualizer/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Data Visualizer    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    1,2,3,4,5
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Protocol Generator
    Open Browser    ${TOOLS_BASE_URL}/biotech/protocol-generator/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Protocol Generator    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    PCR protocol
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Biotech tools test took ${duration} seconds

Logistics Tools Test
    [Documentation]    Test all logistics utility tools
    ${start}=    Get Time    epoch

    # Test Route Optimizer
    Open Browser    ${TOOLS_BASE_URL}/logistics/route-optimizer/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Route Optimizer    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    New York to Los Angeles
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Inventory Tracker
    Open Browser    ${TOOLS_BASE_URL}/logistics/inventory-tracker/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Inventory Tracker    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Item: Widget, Qty: 100
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Shipment Tracker
    Open Browser    ${TOOLS_BASE_URL}/logistics/shipment-tracker/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Shipment Tracker    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Shipment ID: SHIP001
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Warehouse Planner
    Open Browser    ${TOOLS_BASE_URL}/logistics/warehouse-planner/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Warehouse Layout Planner    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Warehouse layout plan
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Logistics tools test took ${duration} seconds

Fintech Tools Test
    [Documentation]    Test all fintech utility tools
    ${start}=    Get Time    epoch

    # Test Budget Calculator
    Open Browser    ${TOOLS_BASE_URL}/fintech/budget-calculator/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Budget Calculator    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Income: 5000, Expenses: 3000
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Investment Tracker
    Open Browser    ${TOOLS_BASE_URL}/fintech/investment-tracker/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Investment Tracker    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Stock: AAPL, Shares: 10
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Invoice Generator
    Open Browser    ${TOOLS_BASE_URL}/fintech/invoice-generator/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Invoice Generator    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Invoice for services
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Crypto Portfolio
    Open Browser    ${TOOLS_BASE_URL}/fintech/crypto-portfolio/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Crypto Portfolio    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    BTC: 0.5, ETH: 2.0
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Fintech tools test took ${duration} seconds

Dev Tools Test
    [Documentation]    Test all software development utility tools
    ${start}=    Get Time    epoch

    # Test Code Snippet Manager
    Open Browser    ${TOOLS_BASE_URL}/dev/code-snippet-manager/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Code Snippet Manager    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    console.log('Hello World');
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test API Tester
    Open Browser    ${TOOLS_BASE_URL}/dev/api-tester/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    API Tester    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    GET /api/users
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Bug Tracker
    Open Browser    ${TOOLS_BASE_URL}/dev/bug-tracker/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Bug Tracker    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Null pointer exception in login
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    # Test Deployment Monitor
    Open Browser    ${TOOLS_BASE_URL}/dev/deployment-monitor/index.html    chrome
    Maximize Browser Window
    Wait Until Page Contains    Deployment Monitor    10s
    Page Should Contain Element    id=inputData
    Input Text    id=inputData    Deployment status check
    Click Button    xpath=//button[contains(text(),"Process")]
    Wait Until Page Contains    Processed data    5s
    Close Browser

    ${end}=    Get Time    epoch
    ${duration}=    Evaluate    ${end}-${start}
    Log    Dev tools test took ${duration} seconds