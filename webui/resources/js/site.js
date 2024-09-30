function toTitleCase(str) {
    return str.toLowerCase().replace(/\b\w/g, s => s.toUpperCase());
}


$(() => {
    $("form").submit(e => {
        e.preventDefault();
        let target = $(e.target);
        let formData = new FormData(e.target);
        console.log(formData);
        $.ajax({
            url: target.attr('action'),
            type: target.attr('method'),
            contentType: false,
            processData: false,
            data: formData,
            success: onFormSuccess,
            error: onFormError,
        })
    });

    $('input[class="file-input"]').change(e => {
        let targ = $(e.target)
        let filepath = targ.val()
        let filename = filepath.replace(/^.*[\\/]/, '')
        targ.siblings('span[class="file-name"]').text(filename);
    });
})
