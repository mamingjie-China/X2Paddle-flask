$(function() {
var onnx_name = '';
var tf_name = '';
var caffe_model_name = '';
var caffe_weight_name = '';
var model_id = '';

layui.use('form', function(){

    var form = layui.form;
  //监听提交
    form.on('submit(form)', function(data){
    var is_ready = true;

    console.log(is_ready)
    data.field['tf_name'] = tf_name;
    data.field['onnx_name'] = onnx_name;
    data.field['caffe_weight_name'] = caffe_weight_name;
    data.field['caffe_model_name'] = caffe_model_name;
    data.field['model_id'] = model_id
      $.ajax({
            type: 'POST',
            url: '/convert',
            data: JSON.stringify(data.field),
            contentType: false,
            processData: false,
            dataType: 'json',
          beforeSend: function () {
                if(!is_ready){
                    return;
                }
//                layui.$("#result").hide();
                layer.load();
          }
        }).success(function(data, textStatus, jqXHR){
            var download_link =  "/download/"+ data['name'];
            if(is_ready && data['status']=='success'){
                layer.msg(data['status']);
                layui.$("#result").show();
                 $("#resultConvertion").attr("href", download_link);
                  $("#resultConvertion").text(data['name']);
                  $("#cmd_result").after(data['cmd_result'])
                 layer.closeAll('loading'); //关闭loading
            }else if(is_ready){
                layer.msg(data['status']);
                 $("#cmd_result").after(data['cmd_result'])
                 layer.closeAll('loading'); //关闭loading
            }
        }).fail(function(){
             layer.closeAll('loading'); //关闭loading
            alert('error!');

        });
    return false;
  });

  form.on('select(filter)', function(data){
  console.log(data.value); //得到被选中的值
      if(data.value == 0){
          layui.$("#tensorflow").show();
          layui.$("#result_upload").hide();
           layui.$("#caffe").hide();
            layui.$("#onnx").hide();
             layui.$("#caffe_weight").hide();
              layui.$("#caffe_model").hide();

      }
      if(data.value == 1){
          layui.$("#tensorflow").hide();
          layui.$("#result_upload").hide();
           layui.$("#caffe").hide();
            layui.$("#onnx").show();
             layui.$("#caffe_weight").hide();
              layui.$("#caffe_model").hide();

      }
      if(data.value == 2){
          layui.$("#tensorflow").hide();
          layui.$("#result_upload").hide();
           layui.$("#caffe_model").show();
           layui.$("#caffe_weight").hide();
             layui.$("#onnx").hide();
      }
      if(data.value == ''){
          layui.$("#tensorflow").hide();
           layui.$("#caffe").hide();
             layui.$("#onnx").hide();
      }
});
});



layui.use(['upload', 'element'], function(){
  var upload = layui.upload;
  element = layui.element;
  // element.init();

  //选完文件后不自动上传
    upload.render({
    elem: '#tf_file'
    ,url: '/upload'
    ,exts: 'pb' //只允许上传pb文件
    ,size: 5120000 //限制文件大小，单位为kb
    ,auto: false
    ,accept: 'file'
    //,multiple: true
    ,bindAction: '#tensorflow_upload'
    ,progress: function (e, percent) {
        console.log("进度：" + percent + '%');
        element.progress('progressBar', percent  + '%');
    }
    ,before: function () {
        layui.$("#progressBar").show();
        layui.$("#result_upload").hide();
        // layui.$("#progressBar").show();
        layer.load();
      }
    ,done: function(res){
        layui.$("#result_upload").show();
        tf_name = res.name;
        model_id = res.name;
        layui.$("#result").hide();
        layui.$("#progressBar").hide();
        layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });

    upload.render({
    elem: '#onnx_file'
    ,url: '/upload'
    ,exts: 'onnx' //只允许上传onnx文件
    ,size: 512000 //限制文件大小，单位为kb
    ,auto: false
    ,accept: 'file'
    //,multiple: true
    ,bindAction: '#onnx_upload'
    ,progress: function (e, percent) {
        console.log("进度：" + percent + '%');
        element.progress('progressBar', percent  + '%');
    }
    ,before: function () {
        layui.$("#progressBar").show();
        layui.$("#result_upload").hide();
        layer.load();
    }
    ,done: function(res){
        layui.$("#result_upload").show();
        onnx_name = res.name;
        model_id = res.name;
        layui.$("#result").hide();
        layui.$("#progressBar").hide();
        layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });

  //   var files = '';
    upload.render({
    elem: '#caffe_model_upload'
    ,url: '/upload'
    ,exts: 'pt|proto|prototxt' //只允许上传prototxt文件
    ,size: 51200 //限制文件大小，单位为kb
    ,auto: false
    ,accept: 'file'
    // ,multiple: true
    ,bindAction: '#caffe_upload_model'
    ,progress: function (e, percent) {
        console.log("进度：" + percent + '%');
        element.progress('progressBar', percent  + '%');
    }
    // ,choose: function(obj){
    // //将每次选择的文件追加到文件队列
    //     files = obj.pushFile();
    //   //delete files[index]; //删除列表中对应的文件，一般在某个事件中使用
    // }
    ,before: function () {
        layui.$("#progressBar").show();
        layui.$("#result_upload").hide();
        layer.load();
    }
    ,done: function(res){
        layui.$("#result_upload").show();
        caffe_model_name = res.name;
        model_id = res.name;
        // layui.$("#caffe_model").hide();
        // layui.$("#caffe_weight").show();
        layer.closeAll('loading'); //关闭loading
        layui.$("#caffe_model").hide();
        layui.$("#result_upload").hide();
        layui.$("#result").hide();
        layui.$("#progressBar").hide();
        layui.$("#caffe_weight").show();
      console.log(res)
    }
  });
  //   var files = '';
    upload.render({
    elem: '#caffe_weight_upload'
    ,url: '/upload'
    ,data: {model_id: model_id}
    ,exts: 'caffemodel' //只允许上传caffemodel文件
    ,size: 512000 //限制文件大小，单位为kb
    ,auto: false
    ,accept: 'file'
    ,multiple: false
    ,bindAction: '#caffe_upload_weight'
    ,progress: function (e, percent) {
        console.log("进度：" + percent + '%');
        element.progress('progressBar', percent  + '%');
    }
    // ,choose: function(obj){
    // //将每次选择的文件追加到文件队列
    //     var files = obj.pushFile();
    //   //delete files[index]; //删除列表中对应的文件，一般在某个事件中使用
    // }
    ,before: function () {
        layui.$("#progressBar").show();
        layui.$("#result_upload").hide();
        layer.load();
        this.data={'model_id':model_id};
    }
    ,done: function(res){
        layui.$("#result_upload").show();
        caffe_model_name = res.name;
        model_id = res.name;
        layui.$("#result").hide();
        layui.$("#progressBar").hide();
        layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });

  // upload.render({
  //   elem: '#caffe_model'
  //   ,url: '/upload'
  //     ,accept: 'file'
  //   //,multiple: true
  //     ,before:function () {
  //         layui.$("#result_upload").hide();
  //         layer.load();
  //     }
  //   ,done: function(res){
  //       layui.$("#result_upload").show();
  //       caffe_model_name = res.name;
  //       layer.closeAll('loading');
  //     console.log(res)
  //   }
  // });
  //   upload.render({
  //   elem: '#caffe_weight'
  //   ,url: '/upload'
  //     ,accept: 'file'
  //   //,multiple: true
  //     ,before:function () {
  //         layui.$("#result_upload").hide();
  //         layer.load();
  //     }
  //   ,done: function(res){
  //       layui.$("#result_upload").show();
  //     caffe_weight_name = res.name;
  //     layer.closeAll('loading'); //关闭loading
  //     console.log(res)
  //   }
  // });
  //   upload.render({
  //   elem: '#onnx_file'
  //   ,url: '/upload'
  //     ,accept: 'file'
  //   //,multiple: true
  //     ,before:function () {
  //         layui.$("#result_upload").hide();
  //         layer.load();
  //     }
  //   ,done: function(res){
  //       layui.$("#result_upload").show();
  //       onnx_name = res.name;
  //       model_id = res.name;
  //       layer.closeAll('loading'); //关闭loading
  //     console.log(res)
  //   }
  // });
  //   upload.render({
  //   elem: '#tf_file'
  //   ,url: '/upload'
  //     ,accept: 'file'
  //   //,multiple: true
  //     ,before:function () {
  //         layui.$("#result_upload").hide();
  //         layer.load();
  //     }
  //   ,done: function(res){
  //       layui.$("#result_upload").show();
  //       tf_name = res.name;
  //       model_id = res.name;
  //       layer.closeAll('loading'); //关闭loading
  //     console.log(res)
  //   }
  // });


})
});
