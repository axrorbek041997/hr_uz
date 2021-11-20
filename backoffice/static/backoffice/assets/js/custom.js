document.getElementById("video-files").addEventListener("change", e => {
    var _files = e.target.files;
    const _div = document.getElementById("video-items");
    for (var i = 0; _files.length; i++) {

        let file = _files[i];
        let blobURL = URL.createObjectURL(file);

        var div1 = document.createElement('div');
        div1.className = 'col-md-3 card';
        div1.style = "width: 18rem;";

        var _video = document.createElement('video');
        _video.className = 'card-img-top';
        _video.src = blobURL;
        _video.controls = "controls";

        var div2 = document.createElement('div');
        div2.className = "card-body";

        var _h5 = document.createElement('h5');
        _h5.className = "card-title";
        _h5.innerText = file.name;

        div2.appendChild(_h5);

        div1.appendChild(_video);
        div1.appendChild(div2);

        _div.appendChild(div1);
    }
});

document.getElementById("pdf-files").addEventListener("change", e => {
    var _files = e.target.files;
    const _div = document.getElementById('file-items');

    for (var i = 0; i < _files.length; i++) {
        var element = _files[i];
        var blobUrl = URL.createObjectURL(element);
        
        console.log(element);

        var my_a = document.createElement('a');
        my_a.href = blobUrl;
        my_a.innerText = element.name;
        my_a.className = "card col-md-3";

        _div.appendChild(my_a);
    }
});

document.getElementById('add-url-button').addEventListener('click', e => {
    document.getElementById('url-name').value = '';
});

document.getElementById("url-save-changes").addEventListener('click', e => {
    var url = document.getElementById('url-name');
    const _div = document.getElementById('url-items');

    var my_a = document.createElement('input');
    my_a.type = "url";
    my_a.name = "urls";
    my_a.value = url.value;
    my_a.readOnly = true;
    my_a.className = "card col-md-3";

    _div.appendChild(my_a);

    $('#exampleModal').modal('hide');
    e.target.disabled = true;
});


var delete_btn = document.getElementById('delete-question')

document.getElementById('add-question').addEventListener('click', e => {
    var add_list = document.getElementById('add-questions');
    var input_list = document.querySelectorAll('input[name="question"]');
    var i = add_list.childElementCount;

    if (input_list[input_list.length - 1].value) {
        var div1 = document.createElement('div');
        div1.className = 'training-item';

        var label = document.createElement('lable')
        label.textContent = ++i + " - savol"

        var q = document.createElement("input")
        q.type = 'text'
        q.className = 'form-control'
        q.name = 'question'
        q.placeholder = 'Savolni kiriting...'

        div1.appendChild(label);
        div1.appendChild(q);

        document.getElementById('add-questions').appendChild(div1);
    }
    var questions = document.querySelectorAll("input[name='question']")

    if (questions.length > 1) {
        delete_btn.hidden = false;
    }

});

delete_btn.addEventListener('click', e => {
    // var questions = document.querySelectorAll("input[name='question']")
    var questions = document.getElementById("add-questions")
    if (questions.childElementCount > 2) {
        questions.removeChild(questions.lastChild)
    } else {
        questions.removeChild(questions.lastChild);
        e.target.hidden = true;
    }
})

document.getElementById('url-name').addEventListener('keyup', e => {
    if (e.target.value.includes('www.youtube.com')) {
        document.getElementById('url-save-changes').disabled = false
    } 
})
