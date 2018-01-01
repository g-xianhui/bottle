<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="http://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js"></script>
<script type="text/javascript">
function request_log(logName)
{
    $.get("/agancmd/log?name="+logName, function (data, status) {
            if (status == "success") {
                console.log(data)
                //$("#txtLog").html(data.txt.replace(/\n/g, "<br>"));
                $("#txtLog").html(data.txt);
                if (data.fin == 0) {
                    setTimeout(function () {
                            request_log(logName);
                            },
                            1000);
                }
            }
    });
}

function request_upload()
{
    $.post("/agancmd/upload", $("#uploadForm").serialize(), function (data, status) {
            console.log(data)
            if (status == "success") {
                if (data == "wait") {
                    $("#txtLog").html("其他人正在上传中，请稍候重试。" )
                } else {
                    request_log(data)
                }
            } else {
                $("#txtLog").html(status)
            }
       });
}
</script>

<style>
.btns { width:50px; height:50px; }
</style>

</head>
<body>

<form id="uploadForm" onsubmit="return false" action="##" method="post" > 
脚本: 
<br><br>
<select name="script">
<option value="test.sh" selected="selected">测试</option>
<option value="test.sh">test</option>
</select>
<br><br>
<button type="submit" class="btns" onclick="request_upload()">提交</button>
</form>

<p>日志: </p>
<pre><span id="txtLog"></span></pre> 

</body>
</html>
