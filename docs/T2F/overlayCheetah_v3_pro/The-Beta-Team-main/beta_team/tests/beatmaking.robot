*** Settings ***
Documentation     Beta Team beatmaking suite for ChordStudio.
...
...               Drives the REAL app over CDP (no mock): pads, banks, the step
...               sequencer, patterns, transport and chop-to-pads all round-trip
...               through the native C++ engine. Run from the Beta Team launcher
...               (scenario: beatmaking) or:
...
...                 python -m robot --variable BUILD_PATH:"<exe>" tests/beatmaking.robot
Library           ${CURDIR}/../sdk/adapters/ChordStudioCdp.py
Library           OperatingSystem
Suite Setup       Start ChordStudio
Suite Teardown    Close App

*** Variables ***
${BUILD_PATH}     ${EMPTY}
${CDP_PORT}       9226

*** Test Cases ***
App Shell And Drums Workspace Load
    [Documentation]    The app launches, the workspace tabs render, and Drums is reachable.
    Dismiss Overlays
    Open Workspace    Drums
    Text Should Be Visible    Drums
    Text Should Not Be Visible    Connecting to engine...
    Screenshot    beatmaking-01-drums

Pad Banks And Pad Selection Respond
    [Documentation]    Banks A-H switch the pad grid, and selecting a pad shows its editor.
    Dismiss Overlays
    Open Workspace    Drums
    Select Pad Bank    H
    Pad Label Should Contain    H16    Pad H16
    Select Pad Bank    A
    Select Pad    A03
    Wait Until Keyword Succeeds    5x    0.3s    Pad Selected    A03
    Text Should Be Visible    PADS

Sequencer Step Toggle Round Trips Through The Engine
    [Documentation]    Toggling a step flips its aria-pressed state, and toggling back restores it.
    Dismiss Overlays
    Open Workspace    Drums
    Select Pad    A01
    Open Sampler Mode    Sequence
    Wait Until Keyword Succeeds    5x    0.3s    Step Exists    A01    1
    ${before}=    Step State    A01    1
    Toggle Step    A01    1
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Differ    A01    1    ${before}
    Toggle Step    A01    1
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Equal    A01    1    ${before}

Pattern Length And Pattern Selection
    [Documentation]    Pattern length extends the grid; patterns select and latch.
    Dismiss Overlays
    Open Workspace    Drums
    Select Pad    A01
    Open Sampler Mode    Sequence
    Set Time Correct    1/16
    Set Pattern Length    2 bars
    Wait Until Keyword Succeeds    5x    0.3s    Step Exists    A01    32
    Select Pattern    2
    Wait Until Keyword Succeeds    5x    0.3s    Pattern State Should Be   2    on

Transport Play And Stop
    [Documentation]    The transport starts and stops the sequencer.
    Dismiss Overlays
    Open Workspace    Drums
    Open Sampler Mode    Sequence
    Transport    play
    Wait Until Keyword Succeeds    5x    0.3s    Transport State Should Be    play    on
    Transport    stop
    Wait Until Keyword Succeeds    5x    0.3s    Transport State Should Be    play    off

Chop A Sample Into Pads
    [Documentation]    Drop a WAV on a pad, detect slices, and assign them to pads.
    ...    NOTE: this loads a sample into the session (pad H16); it is the one
    ...    test here that mutates state.
    Dismiss Overlays
    Open Workspace    Drums
    Select Pad Bank    H
    Select Pad    H16
    ${wav}=    Make Transient Wav Base64
    Drop Sample On Pad    H16    E2EChop.wav    ${wav}
    Wait Until Keyword Succeeds    5x    0.3s    Pad Label Should Contain    H16    E2EChop
    Open Sampler Mode    Chop
    Text Should Be Visible    SLICES
    Chop To Pads
    Screenshot    beatmaking-02-chop

A Sequencer Control Responds To A Real Drag
    [Documentation]    The Swing control responds through the engine. Driven by the
    ...    APG keyboard contract (End=max, Home=min) because synthetic CDP mouse
    ...    drags coalesce unreliably; both paths call the same onChange -> engine.
    ...    MPC swing spans 50-75%, so max is 75 and min is 50.
    Dismiss Overlays
    Open Workspace    Drums
    Open Sampler Mode    Sequence
    Press Control Key    Swing    End
    Wait Until Keyword Succeeds    5x    0.3s    Control Value Should Be    Swing    75
    Press Control Key    Swing    Home
    Wait Until Keyword Succeeds    5x    0.3s    Control Value Should Be    Swing    50

Make A Beat Using The App's Functions
    [Documentation]    Build a real beat end to end: load kick/snare/hat one-shots onto
    ...    pads, program a 16-step pattern on the grid, set the time-correct grid,
    ...    play it, then build a second 32-step pattern, add swing and a chain,
    ...    and play the result. Every edit round-trips through the native engine.
    Dismiss Overlays
    Open Workspace    Drums
    Select Pad Bank    A

    # 1. Load a drum kit we synthesise ourselves (kick / snare / hat).
    ${kick}=    Make Oneshot Base64    kick
    Drop Sample On Pad    A01    KICK.wav    ${kick}
    Wait Until Keyword Succeeds    5x    0.3s    Pad Label Should Contain    A01    KICK
    ${snare}=    Make Oneshot Base64    snare
    Drop Sample On Pad    A02    SNARE.wav    ${snare}
    Wait Until Keyword Succeeds    5x    0.3s    Pad Label Should Contain    A02    SNARE
    ${hat}=    Make Oneshot Base64    hat
    Drop Sample On Pad    A03    HAT.wav    ${hat}
    Wait Until Keyword Succeeds    5x    0.3s    Pad Label Should Contain    A03    HAT

    # 2. Program pattern 1 on the 1/16 grid: kick 1/9/13, snare 5/13, hats on the offbeats.
    Open Sampler Mode    Sequence
    Select Pattern    1
    Set Time Correct    1/16
    Set Pattern Length    1 bar
    FOR    ${s}    IN    1    9    13
        Ensure Step    A01    ${s}    on
    END
    FOR    ${s}    IN    5    13
        Ensure Step    A02    ${s}    on
    END
    FOR    ${s}    IN    1    3    5    7    9    11    13    15
        Ensure Step    A03    ${s}    on
    END
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Equal    A01    9    on
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Equal    A02    5    on
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Equal    A03    15    on

    # 3. Play the beat, then stop.
    Transport    play
    Wait Until Keyword Succeeds    5x    0.3s    Transport State Should Be    play    on
    Sleep    1.5s
    Transport    stop
    Wait Until Keyword Succeeds    5x    0.3s    Transport State Should Be    play    off

    # 4. A second, longer pattern (32 steps) and switch back to pattern 1.
    Select Pattern    2
    Set Time Correct    1/16
    Set Pattern Length    2 bars
    FOR    ${s}    IN    1    9    17    25
        Ensure Step    A01    ${s}    on
    END
    FOR    ${s}    IN    5    13    21    29
        Ensure Step    A02    ${s}    on
    END
    Wait Until Keyword Succeeds    5x    0.3s    Pattern State Should Be    2    on
    Select Pattern    1
    Wait Until Keyword Succeeds    5x    0.3s    Pattern State Should Be    1    on
    Wait Until Keyword Succeeds    5x    0.3s    Step State Should Equal    A01    1    on

    # 5. Feel: add swing, then chain pattern 1 -> 2.
    Press Control Key    Swing    End
    Wait Until Keyword Succeeds    5x    0.3s    Control Value Should Be    Swing    75
    Click Button Containing    + Pattern

    Screenshot    beatmaking-03-beat
    Text Should Be Visible    SEQUENCE

*** Keywords ***
Start ChordStudio
    Set Environment Variable    ROBOT_OUTPUT_DIR    ${OUTPUT DIR}
    IF    len($BUILD_PATH) > 0
        Launch App    ${BUILD_PATH}    ${CDP_PORT}
    ELSE
        Launch App    port=${CDP_PORT}
    END

Step State Should Differ
    [Arguments]    ${pad}    ${step}    ${other}
    ${now}=    Step State    ${pad}    ${step}
    Should Not Be Equal    ${now}    ${other}

Step State Should Equal
    [Arguments]    ${pad}    ${step}    ${expected}
    ${now}=    Step State    ${pad}    ${step}
    Should Be Equal    ${now}    ${expected}

Pattern State Should Be
    [Arguments]    ${index}    ${expected}
    ${now}=    Pattern State    ${index}
    Should Be Equal    ${now}    ${expected}

Transport State Should Be
    [Arguments]    ${action}    ${expected}
    ${now}=    Transport State    ${action}
    Should Be Equal    ${now}    ${expected}

Control Value Should Be
    [Arguments]    ${label}    ${expected}
    ${now}=    Control Value    ${label}
    Should Be Equal As Integers    ${now}    ${expected}
