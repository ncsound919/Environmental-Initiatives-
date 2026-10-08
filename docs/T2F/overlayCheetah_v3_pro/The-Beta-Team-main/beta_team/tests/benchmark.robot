*** Settings ***
Documentation     Beta Team benchmark suite for ChordStudio.
...
...               Times the app's core operations against the real engine and
...               records wall-clock marks plus the app process's memory and CPU.
...               Writes ${OUTPUT DIR}/benchmark.json for the Beta Team dashboard.
Library           ${CURDIR}/../sdk/adapters/ChordStudioCdp.py
Library           OperatingSystem
Suite Setup       Start Bench
Suite Teardown    End Bench

*** Variables ***
${BUILD_PATH}     ${EMPTY}
${CDP_PORT}       9227

*** Test Cases ***
Measure Generate
    [Documentation]    Time a full progression generation.
    Dismiss Overlays
    Generate Progression
    Benchmark Mark    generate_progression
    ${n}=    Chord Count
    Should Be True    ${n} >= 8    Generate produced only ${n} chords

Measure Audition
    [Documentation]    Time auditioning the selected chord.
    Audition Chord
    Benchmark Mark    audition_chord

Measure Song Play
    [Documentation]    Time transport start plus a short play window.
    Song Transport    play
    Wait Until Keyword Succeeds    6x    0.4s    Song Should Be Playing
    Sleep    1.0s
    Song Transport    stop
    Benchmark Mark    song_play_stop

Measure Drum Program
    [Documentation]    Time programming a four-hit pattern on the step grid.
    Open Workspace    Drums
    Open Sampler Mode    Sequence
    Select Pattern    1
    Set Pattern Length    16
    Set Time Correct    1/16
    FOR    ${s}    IN    1    5    9    13
        Ensure Step    A01    ${s}    on
    END
    Benchmark Mark    drum_program

Measure Synth Engine Switch
    [Documentation]    Time switching the synth engine.
    Select Synth Engine    Analog
    Benchmark Mark    synth_engine_switch

App Survives The Benchmark
    [Documentation]    The app is still alive and answering after the whole run.
    App Should Be Alive

*** Keywords ***
Start Bench
    Set Environment Variable    ROBOT_OUTPUT_DIR    ${OUTPUT DIR}
    Benchmark Start
    IF    len($BUILD_PATH) > 0
        Launch App    ${BUILD_PATH}    ${CDP_PORT}
    ELSE
        Launch App    port=${CDP_PORT}
    END
    Benchmark Mark    launch_and_attach

End Bench
    Benchmark Mark    total
    Benchmark Report    ${OUTPUT DIR}/benchmark.json
    Close App

Song Should Be Playing
    ${state}=    Song Playing
    Should Be Equal    ${state}    on

App Should Be Alive
    ${alive}=    App Alive
    Should Be True    ${alive}
