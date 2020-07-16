# EasyLabel
### Basic Usage
1. Run `python template.py path/to/folder` to generate an empty label file containing the template of all videos in your `path/to/folder`.      
_The initial file will be like below:_
```
~~~~~~~~~~ video_1.mp4 ~~~~~~~~~~~
(VIEW)
(TIME)


~~~~~~~~~~ video_2.mp4 ~~~~~~~~~~~
(VIEW)
(TIME)

```
2. Run `python translate.py path/to/label.txt` to translate the label.txt to an json file.      
_Example output_
```
{
    "video_1.mp4": {
        "time": "4,8",
        "view": "1",
        "questions": [
            {
                "question": "This is an descriptive question? ",
                "options": [
                    "this is the 1th option",
                    "this is the 2nd option",
                    "this is the 3rd option"
                ],
                "answers": [
                    "B"
                ],
                "type": "Descriptive"
            }
        ]
    },
    "video_2.mp4": {
        "time": "",
        "view": "3",
        "questions": [
            {
                "question": "This is an expanatory question? ",
                "options": [
                    "i'am option A",
                    "i'am option B",
                    "i'am option C",
                    "i'am option D"
                ],
                "answers": [
                    "A",
                    "D"
                ],
                "type": "Explanatory"
            }
        ]
    }
}
```

### Label File Convention
Our translator requires a special and simple syntax, **you need to read the example carefully and fully understand our convention**.  
<pre>
// an example of our label file.
// "//" is used for comments

~~~~~~~ video_0.mp4 ~~~~~~~~~
(VIEW) 3
(TIME) 12, 17

Why the white car stopped? e
the drive fall in sleep
+waiting for the traffic light
+waiting for pedistrians to pass

What is the color of the car in front?
white
+black
orange


~~~~~~~ video_1.mp4 ~~~~~~~~~
(VIEW) 1                        
// point of view (1/3)?

(TIME) 4,8
// used for <b>re-trimming</b> the video 
// it is used for two purpose:
// 1. the video is <i>badly trimmed</i> and needs to be trimmed again
// 2. you want to ask a <i>Predictive</i> or <i>Reverse Inference</i> question

This is an descriptive question? d
// every question MUST <b>end with a <i>"?" </i>(QUESTION MARK)</b>
// after the "?", a <b>letter</b> or <b>number</b> is needed to
// descripe which category the question belongs to.

// 'd' or 1 -> Descriptive
// 'e' or 2 -> Explanatory
// 'p' or 3 -> Predictive
// 'r' or 4 -> Reverse Inference
// 'c' or 5 -> Counterfactual
// 'i' or 6 -> Introspection


this is the 1th option
<b>+</b>this is the 2nd option 
this is the 3rd option
// options follow each question
// if an option is correct, put a <b>+(PLUS)</b> at the beginning




~~~~~~~ video_2.mp4 ~~~~~~~~~~
(VIEW) 3
(TIME)
// if nothing follows "(TIME)", <b>the entire video will be keept</b>

This is an expanatory question? e

+i'am option A
i'am option B
i'am option C
+i'am option D

<pre>
