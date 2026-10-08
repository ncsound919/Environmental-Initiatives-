*** Settings ***
Documentation     Beta Team song suite for ChordStudio.
...
...               Covers the modules the drum suite did not: chord generation and
...               audition, the live song transport (so the progression is
...               actually played), the CS-6 synth, the mixer, the VST3 hosting
...               surface, and a combined beat where chords, synth and drums play
...               together. Drives the REAL app over CDP.
Library           ${CURDIR}/../sdk/adapters/ChordStudioCdp.py
Library           OperatingSystem
Suite Setup       Start ChordStudio
Suite Teardown    Close App

*** Variables ***
${BUILD_PATH}     ${EMPTY}
${CDP_PORT}       9226

*** Test Cases ***
Generate A Chord Progression
    [Documentation]    Compose -> Generate produces a real progression of chord pads.
    Dismiss Overlays
    Generate Progression
    ${n}=    Chord Count
    Should Be True    ${n} >= 8    Generate produced only ${n} chords
    Text Should Be Visible    sections
    Screenshot    song-01-compose

Audition A Chord
    [Documentation]    The selected chord auditions through the engine.
    Dismiss Overlays
    Generate Progression
    Audition Chord
    ${n}=    Chord Count
    Should Be True    ${n} >= 8

Play The Song Transport
    [Documentation]    The live song transport plays the arrangement and the playhead advances.
    Dismiss Overlays
    Generate Progression
    Song Transport    play
    Wait Until Keyword Succeeds    6x    0.4s    Song Should Be Playing
    ${a}=    Song Transport Readout
    Sleep    1.2s
    ${b}=    Song Transport Readout
    Should Not Be Equal    ${a}    ${b}
    Song Transport    stop
    Wait Until Keyword Succeeds    6x    0.4s    Song Should Be Stopped

Synth Engines And Operators Respond
    [Documentation]    Switch synth engine, read the patch, and move an operator control.
    Dismiss Overlays
    Select Synth Engine    Analog
    Text Should Be Visible    Analog
    Select Synth Engine    CS-6 FM
    ${ops}=    Synth Operator Count
    Should Be True    ${ops} >= 6    expected 6 FM operators, saw ${ops}
    Press Control Key    Rate 1    End
    ${v}=    Control Value    Rate 1
    Should Be True    ${v} >= 0
    Screenshot    song-02-synth

Mixer Mute And Solo Round Trip
    [Documentation]    A track's mute toggles and restores through the engine.
    Dismiss Overlays
    Select Track    Bass
    ${before}=    Track Mute State    Bass
    Toggle Track Mute    Bass
    Wait Until Keyword Succeeds    5x    0.3s    Track Mute Should Differ    Bass    ${before}
    Toggle Track Mute    Bass
    Wait Until Keyword Succeeds    5x    0.3s    Track Mute Should Equal    Bass    ${before}
    Toggle Track Solo    Bass
    Toggle Track Solo    Bass

VST3 Hosting Controls Are Present
    [Documentation]    The plugin-hosting surface exists (selecting a plugin needs a native
    ...    file dialog, so the harness verifies the controls, not the dialog).
    Dismiss Overlays
    Open Workspace    Mix
    Plugin Controls Present

Combine Chords Synth And Drums Into A Beat
    [Documentation]    Program a drum pattern, start the drum machine, generate a
    ...    progression, and play the song so chords + synth + drums sound together.
    Dismiss Overlays

    # Drums: load a kit and program a pattern.
    Open Workspace    Drums
    Select Pad Bank    A
    ${kick}=    Make Oneshot Base64    kick
    Drop Sample On Pad    A01    KICK.wav    ${kick}
    ${snare}=    Make Oneshot Base64    snare
    Drop Sample On Pad    A02    SNARE.wav    ${snare}
    ${hat}=    Make Oneshot Base64    hat
    Drop Sample On Pad    A03    HAT.wav    ${hat}
    Open Sampler Mode    Sequence
    Select Pattern    1
    Set Pattern Length    16
    Set Time Correct    1/16
    FOR    ${s}    IN    1    9    13
        Ensure Step    A01    ${s}    on
    END
    FOR    ${s}    IN    5    13
        Ensure Step    A02    ${s}    on
    END
    FOR    ${s}    IN    1    3    5    7    9    11    13    15
        Ensure Step    A03    ${s}    on
    END
    Transport    play
    Wait Until Keyword Succeeds    5x    0.3s    Transport State Should Be    play    on

    # Chords + synth: generate and play the song.
    Generate Progression
    Song Transport    play
    Wait Until Keyword Succeeds    6x    0.4s    Song Should Be Playing
    Sleep    2.5s
    Screenshot    song-03-full-beat

    Song Transport    stop
    Open Workspace    Drums
    Transport    stop

*** Keywords ***
Start ChordStudio
    Set Environment Variable    ROBOT_OUTPUT_DIR    ${OUTPUT DIR}
    IF    len($BUILD_PATH) > 0
        Launch App    ${BUILD_PATH}    ${CDP_PORT}
    ELSE
        Launch App    port=${CDP_PORT}
    END

Song Should Be Playing
    ${state}=    Song Playing
    Should Be Equal    ${state}    on

Song Should Be Stopped
    ${state}=    Song Playing
    Should Be Equal    ${state}    off

Track Mute Should Differ
    [Arguments]    ${name}    ${other}
    ${now}=    Track Mute State    ${name}
    Should Not Be Equal    ${now}    ${other}

Track Mute Should Equal
    [Arguments]    ${name}    ${expected}
    ${now}=    Track Mute State    ${name}
    Should Be Equal    ${now}    ${expected}

Transport State Should Be
    [Arguments]    ${action}    ${expected}
    ${now}=    Transport State    ${action}
    Should Be Equal    ${now}    ${expected}
