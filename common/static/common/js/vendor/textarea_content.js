bkLib.onDomLoaded(function() {
nicEditors.editors.push(
    new nicEditor({iconsPath : '/static/common/js/vendor/nicEditorIcons.gif',
        buttonList : ['fontSize','fontFamily','bold','italic',
            'underline','strikeThrough','left','center','right','justify',
            'ol','ul','subscript','superscript','hr','link','unlink','forecolor']
    }).panelInstance(
        document.getElementById('id_content')
    )
);
});
