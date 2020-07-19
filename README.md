# EasyLabel

### 1. To label which perspective the video is being shot at

- A video can be either 1st-person perspective or 3rd-person perspective
    - 1st-person perspective includes any of these scenarios:
        - The camera is mounted inside a car, and the car itself is directly involved in an accident, including the car hit another car, and the car is hit by another car.
        - The camera is handheld, but whoever holding the camera is directly involved in the event / car crash / accident.
    - 3rd-person perspective includes any of these scenarios:
        - The camera is mounted inside a car, and it is observing an accident happening on other cars but not itself.
        - The camera is handheld by a pedestrian, and it is observing an accident from distance.
        - The camera is a stationary CCTV camera mounted over the head.
- The `qa_label_template.txt` has this line for every video section.
    ```
    <PERSPECTIVE>: {{  }}
    ```
- Just use number `1` or `3` to indicate 1st-person perspective or 3rd-person perspective.
- Example:
    - `<PERSPECTIVE>: {{ 1 }}`
    - `<PERSPECTIVE>: {{ 3 }}`

### 2. Check if the video requires re-trimming refinement

- If the start and the end of the video clip show any frame from adjacent events from the original video compilation, we need to re-trim the video to remove the unrelated portion.
- To re-trim, just provide the `START_TS` (starting timestamp) and the `END_TS` (ending timestamp) **of the part of the video that we want to keep**.
- The `qa_label_template.txt` has this line for every video section.
    ```
    <RE_TRIM>: {{ START_TS, END_TS }}
    ```
- `START_TS` and `END_TS` should strictly follow the [Time Format](#time-format).
- If no re-trimming is needed, leave the line `{{ START_TS, END_TS }}` as it is.

### Time Format

- Sexagesimal (HOURS:MM:SS.MILLISECONDS).
- Most common format would be: `MM:SS`
    - Example:
        - `00:12` interpreted as 12 seconds
        - `01:23` interpreted as 1 minute, 23 seconds
- If you want to be precise on the trimming point, especially for `<CRITICAL_POINT>`, because some accidents happen in a fraction of a second, you can use `MM:SS.MILLISECONDS`
    - Example:
        - `3` interpreted as 3 seconds.
        - `15.6` interpreted as 15.6 seconds.
        - `15.25` interpreted as 15 seconds and 1/4 second.
        - `02:30.05` interpreted as 2 minutes, 30 seconds, and 5/100 of a second.
        - `02:30.189` interpreted as 2 minutes, 30 seconds, and 189/1000 of a second.



If a fraction is used, such as 02:30.05, this is interpreted as "5 100ths of a second", not as frame 5.

For instance, 02:30.5 would be 2 minutes, 30 seconds, and a half a second.

### 3. Provide the critical timestamp for `Predictive` or `Reverse Inference` type of question.

- If you want to ask either `Predictive` or `Reverse Inference` type of question to a video, you would need to cut the video in half, because only half of the video is shown to the DL Model, while the other half of the video will be reserved as a proof of the answer.
- The **critical timestamp** or the **critical point** is where you want to cut the video, you only need to provide a single `TS` (timestamp), our script will later cut the video into two parts:
    1. from video start to `TS`
    2. from `TS` to video end.
- The `qa_label_template.txt` has this line for every video section.
    ```
    <CRITICAL_POINT>: {{ TS }}
    ```
- Replace `TS` with a timestamp that follows [Time Format](#time-format), or leave it as it is if this video does not have `Predictive` nor `Reverse Inference` question type.

*Special notes:*
- Each video should only have either one `Predictive` or `Reverse Inference`, not both.
- Which part of the video will be used as question will be determined by the question type.
    - If `Predictive`, first part of the video will be used as `question video`.
    - if `Reverse Inference`, the second part of the video will be used as `question video`.
- When there is a `<CRITICAL_POINT>` present, other questions under that video should only based on the `question video`.
- When `<RE_TRIM>` and `<CRITICAL_POINT>` both present, the timestamp of the `<CRITICAL_POINT>` should still based on original video timeline, hence, the `<CRITICAL_POINT>` timestamp should between `START_TS` and `END_TS`, otherwise it will be flagged out as error.

### 4. Ask a question

- Each question section looks like this:
    ```
    --------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
    <QASet_ID>: {{ None }}
    <ANS>: {{  }}
    ```
- On each question's first line, fill in the question type in the double curly braces:
    - use `1` or `d` for *Descriptive*.
    - use `2` or `e` for *Explanatory*.
    - use `3` or `p` for *Predictive*.
    - use `4` or `r` for *Reverse Inference*.
    - use `5` or `c` for *Counterfactual*.
    - use `6` or `i` for *Introspection*.
- On the second line, this is used for `QASet` substitution, leave it as it is or see [Advance Usage].
- On the third line, label the correct answer for the question.
    - Each question should have 2 to 5 options. (Only at extreme cases, we support up to 7 options)
        - use `a` or `A` for choosing the first option as the correct answer.
        - use `b` or `B` for choosing the first option as the correct answer.
        - ...
        - use `e` or `E` for choosing the first option as the correct answer.
    - Multiple correct answers are also supported.
        - use `ab` to represent both the first and the second options are correct answer.
    - Examples:
        - `<ANS>: {{ c }}` // lower case is acceptable
        - `<ANS>: {{ B }}` // upper case is acceptable
        - `<ANS>: {{ad}}`      // with or without whitespace is acceptable
        - `<ANS>: {{ e c b }}` // alphabets not in order is acceptable



### `qa_label_template.txt` Example

```
~~~~~~~~~~~~~~~~~~~~ 127411s7T7_clip_039 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<LENGTH> 1.74s
<DIM> (W)1920 x (H)1080
<PERSPECTIVE>: {{  }}
<RE_TRIM>: {{ START_TS, END_TS }}
<CRITICAL_POINT>: {{ TS }}

--------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}


--------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}


--------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}


--------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}


--------------------{{  }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{  }}
```

### Completed Label `.txt` File Example

```
~~~~~~~~~~~~~~~~~~~~ 127411s7T7_clip_039 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<LENGTH> 1.74s
<DIM> (W)1920 x (H)1080
<PERSPECTIVE>: {{ 3 }}
<RE_TRIM>: {{ 00:02, 00:15 }}
<CRITICAL_POINT>: {{ 00:12 }}

--------------------{{ d }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{ a }}
Did a person cross the road in the video?
yes
no

--------------------{{ d }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{ d }}
How many cars were involved in the accident?
only one
two
three to five
more than five


--------------------{{ d }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{ c }}
What's the colour of the traffic light when the car pass under?
green
yellow
red
no traffic light

--------------------{{ e }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{ a }}
What kind of accident happened in the video?
Rear-end
side-collision
road-departure
head-on

--------------------{{ p }} // Q Type: use [1-6]|[d|e|p|r|c|i]
<QASet_ID>: {{ None }}
<ANS>: {{ b }}
is the car on the right going to change lane?
yes
no

```
