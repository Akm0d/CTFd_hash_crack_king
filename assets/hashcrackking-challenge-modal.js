$('#submit-key').unbind('click');
$('#submit-key').click(function (e) {
    e.preventDefault();
    submitkey($('#chal-id').val(), $('#answer-input').val(), $('#nonce').val())
});

$("#answer-input").keyup(function(event){
    if(event.keyCode === 13){
        $("#submit-key").click();
    }
});

$(".input-field").bind({
    focus: function() {
        $(this).parent().addClass('input--filled' );
        $label = $(this).siblings(".input-label");
    },
    blur: function() {
        if ($(this).val() === '') {
            $(this).parent().removeClass('input--filled' );
            $label = $(this).siblings(".input-label");
            $label.removeClass('input--hide' );
        }
    }
});

var data = $.get(script_root + 'admin/chal/' + $('#chal-id').val(), function(obj){
    // Replace [HASH] and [KING] with current values
    var content = $('.chal-desc').text().replace(/\[HASH]/g, obj.current_hash).replace(/\[KING]/g, obj.king);
    $('<textarea/>').html(content).val();

    $('.chal-desc').html(marked(content, {'gfm':true, 'breaks':true}));

    // Replace [KING] in the title with the king of the challenge
    var title = $('.chal-name').text().replace(/\[KING]/g, obj.king);
    $('<textarea/>').html(title).val();
    $('.chal-name').html(marked(title, {'gfm':true, 'breaks':true}));
});
