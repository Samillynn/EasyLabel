# easylabeltool

# Usage

1. Install this package
    ```bash
    pip3 install --upgrade easylabeltool
    ```

2. Check your Label file
    ```bash
    check "YOUR LABEL FILE PATH HERE"
    ```

    *Example*

    This will validate your label file `qa_label_template.txt`
    ```bash
    check bilibili_003/qa_label_template.txt
    ```

3. Parse your Label file
    ```bash
    parse "YOUR LABEL FILE PATH HERE"
    ```

    *Example*

    This will validate and export your label file `qa_label_template.txt` into `.json` format
    ```bash
    parse bilibili_003/qa_label_template.txt
    ```

4. Uninstall this package
    ```bash
    pip3 uninstall easylabeltool
    ```
