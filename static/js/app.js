$(function() {
var onnx_name = '';
var tf_name = '';
var caffe_model_name = '';
var caffe_weight_name = '';

layui.use('form', function(){

    var form = layui.form;
  //监听提交
    form.on('submit(form)', function(data){
    var is_ready = true;
    if(data.field.framework == 0 && tf_name == ''){
        layer.msg('请上传.pb文件');
        is_ready = false;
    }
    if(data.field.framework == 1 && onnx_name == ''){
        layer.msg('请上传.onnx文件');
        is_ready = false;
    }
    if(data.field.framework == 2 ){
        if (caffe_model_name == '' && caffe_weight_name ==''){
            layer.msg('请上传.prototxt和.caffemodel文件');
            is_ready = false;
        }
        else if(caffe_model_name == ''){
            layer.msg('请上传.prototxt文件');
            is_ready = false;
        }
        else if(caffe_weight_name == ''){
            layer.msg('请上传.caffemodel文件');
            is_ready = false;
        }
    }
    console.log(is_ready)
    data.field['tf_name'] = tf_name;
    data.field['onnx_name'] = onnx_name;
    data.field['caffe_weight_name'] = caffe_weight_name;
    data.field['caffe_model_name'] = caffe_model_name;
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
                layui.$("#result").hide();
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
           layui.$("#caffe").hide();
            layui.$("#onnx").hide();
      }
      if(data.value == 1){
          layui.$("#onnx").show();
           layui.$("#caffe").hide();
            layui.$("#tensorflow").hide();
      }
      if(data.value == 2){
          layui.$("#caffe").show();
           layui.$("#tensorflow").hide();
            layui.$("#onnx").hide();
      }
      if(data.value == ''){
          layui.$("#caffe").hide();
           layui.$("#tensorflow").hide();
            layui.$("#onnx").hide();
      }
});
});

layui.use('upload', function(){
  var upload = layui.upload;
  upload.render({
    elem: '#caffe_model'
    ,url: '/test'
      ,accept: 'file'
    //,multiple: true
      ,before:function () {
          layui.$("#result_upload").hide();
          layer.load();
      }
    ,done: function(res){
        layui.$("#result_upload").show();
        caffe_model_name = res.name;
        layer.closeAll('loading');
      console.log(res)
    }
  });
    upload.render({
    elem: '#caffe_weight'
    ,url: '/upload'
      ,accept: 'file'
    //,multiple: true
      ,before:function () {
          layui.$("#result_upload").hide();
          layer.load();
      }
    ,done: function(res){
        layui.$("#result_upload").show();
      caffe_weight_name = res.name;
      layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });
    upload.render({
    elem: '#onnx_file'
    ,url: '/upload'
      ,accept: 'file'
    //,multiple: true
      ,before:function () {
          layui.$("#result_upload").hide();
          layer.load();
      }
    ,done: function(res){
        layui.$("#result_upload").show();
        onnx_name = res.name;
        layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });
      upload.render({
    elem: '#tf_file'
    ,url: '/upload'
      ,accept: 'file'
    //,multiple: true
        ,before:function () {
          layui.$("#result_upload").hide();
          layer.load();
      }
    ,done: function(res){
        layui.$("#result_upload").show();
        tf_name = res.name;
        layer.closeAll('loading'); //关闭loading
      console.log(res)
    }
  });
})
});
