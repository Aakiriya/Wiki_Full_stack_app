tinymce.init({
    selector: 'textarea#default',
    width: 1000,
    height: 400,
  
    plugins: [
      'advlist', 'autolink', 'link', 'image', 'lists', 'charmap', 'prewiew', 'anchor', 'pagebreak',
      'searchreplace', 'wordcount', 'visualblocks', 'fullscreen', 'insertdatetime', 'media',
      'table', 'emoticons', 'template', 'codesample'
    ],
    toolbar: 'undo redo | styles | bold italic underline | alignleft aligncenter alignright alignjustify |' +
      'bullist numlist outdent indent | link image | print preview media fullscreen | ' +
      'forecolor backcolor emoticons',
    menu: {
      favs: {
        title: 'Menu',
        items: ' searchreplace | emoticons'
      }
    },
    menubar: 'favs file edit view insert format tools table',
    content_style: 'body{font-family:Helvetica,Arial,sans-serif; font-size:16px}',
    
    promotion: false,
  

    
    setup: function (editor) {
      var form = document.getElementsByTagName('form')[0];
      var downloadButton = document.getElementById('download-button');
      downloadButton.onclick = function () {
        var title = document.getElementById('title').value || 'content';
        var htmlContent = editor.getContent({ format: 'html' });
        var blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
        var link = document.createElement('a');
        link.download = title + '.html';
        link.href = window.URL.createObjectURL(blob);
        link.click();
      };
  
      var uploadButton = document.getElementById('upload-button');
      uploadButton.onclick = function () {
        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'text/html';
        fileInput.style.display = 'none';
        fileInput.onchange = function () {
          var file = fileInput.files[0];
          var reader = new FileReader();
          reader.onload = function () {
            editor.setContent(reader.result);
          };
          reader.readAsText(file);
        };
        fileInput.click();
      };
    }
  });
  