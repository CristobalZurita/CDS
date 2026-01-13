import React from 'react';
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";
import {CKEditor} from "@ckeditor/ckeditor5-react";
import type {EventInfo} from "@ckeditor/ckeditor5-utils";
import {data} from "autoprefixer";

interface Props {
    data: string;
    onChange: (event: EventInfo<string, unknown>, editor: ClassicEditor) => void;
    id: string
}

function RichTextEditor({onChange, data, id = "description"}:Props) {
    return (
        <CKEditor
            id={id}
            editor={ClassicEditor}
            data={data}
            onChange={onChange}

            config={{
                toolbar: ['undo', 'redo', '|', 'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote']
            }}

            onReady={(editor) => {
                editor.editing.view.change(writer => {
                    // @ts-ignore
                    writer.setStyle('height', '120px', editor.editing.view.document.getRoot());
                })
            }}
        />
    );
}

export default RichTextEditor;
