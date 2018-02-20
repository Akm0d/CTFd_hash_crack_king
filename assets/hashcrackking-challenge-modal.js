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

var data = $.get(script_root + '/hash_crack_king/' + $('#chal-id').val(), function(chal){
    var content = $('.chal-desc').text()
        // Replace [HASH] with the current hash
        .replace(/\[HASH]/g, chal.current_hash)
        // Replace [KING] with the current king
        .replace(/\[KING]/g, chal.king)
        // Replace [MIN] with the number of minutes in a cycle
        .replace(/\[MIN]/g, chal.cycles)
        // Replace [HOLD] with the number of points per cycle
        .replace(/\[HOLD]/g, chal.hold);
    $('<textarea/>').html(content).val();

    $('.chal-desc').html(marked(content, {'gfm':true, 'breaks':true}));

    // Replace [KING] in the title with the king of the challenge
    var title = $('.chal-name').text().replace(/\[KING]/g, chal.king);
    $('<textarea/>').html(title).val();
    $('.chal-name').html(marked(title, {'gfm':true, 'breaks':true}));

    var footer = "\\* " + chal.king + " receives " +  chal.hold + " point(s) every " + chal.cycles + " minute(s)";
    $('<textarea/>').html(footer).val();
    $('.chal-footer').html(marked(footer, {'gfm':true, 'breaks':true}));

});
