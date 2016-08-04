$(document).ready(function() {
    var $loadingGif = $('#loader');
    var $codeContent = $('#code-content');

    function changeCodeContent() {
        
        $loadingGif.show();
        $codeContent.hide()

        $.ajax('/random_code', {
            'dataType': 'html'
        }).done(function(data) {
            $loadingGif.hide();
            $('#code-content').html(data);
            PR.prettyPrint();
            $codeContent.show();
        });
    }

    changeCodeContent();
    $('#new-script-button').on('click', changeCodeContent);

});