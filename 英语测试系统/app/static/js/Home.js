window.onload=function()
{
    $("#word").focus();
    /*var sUl=$(".slider-u");

    var cUl=$(".contro").get(0);
    var cLi=cUl.getElementsByTagName("li");
    for(var i=0; i<cLi.length; i++)
    {
        cLi[i].index=i;

        cLi[i].onclick=function()
        {

            for(var i=0; i<cLi.length; i++)
            {
                cLi[i].setAttribute("id","");
            }
            this.setAttribute("id","active");

            //$(sUl).get(0).style.top=-300*this.index+"px";

            $(sUl).animate({top:this.index*-300});

        }
    }

    var gog=0;
    setInterval(function()
    {
        for(var i=0; i<cLi.length; i++)
        {
            cLi[i].setAttribute("id","");
        }
        cLi[gog].setAttribute("id","active");

        if(gog<2)
        {
            gog=gog+1;
            $(sUl).animate({top:gog*-300});
        }
        else
        {
            gog=0;
            $(sUl).animate({top:gog*-300});

        }
    },1000);*/

    //login
    $("#loginbtn").click(function()
    {
        $.ajax({
            type: 'get',
            url:'/searchUser',
            dataType: 'json',
            success:function (data) {
                console.log(data);
                if(data.status == 'success'){
                    $('#login2').html(data.username);
                    if($(".login1").css("top")==70+"px")
                        {
                            $(".login1").animate({top:"-40em"});
                        }
                        else
                        {
                            $(".login1").animate({top:"5em"});
                        }
                }else{
                    if($(".login").css("top")==70+"px")
                        {
                            $(".login").animate({top:"-40em"});
                        }
                        else
                        {
                            $(".login").animate({top:"5em"});
                        }
                }
            },
            error:function () {
                if($(".login").css("top")==70+"px")
                {
                    $(".login").animate({top:"-40em"});
                }
                else
                {
                    $(".login").animate({top:"5em"});
                }
            }
        });

        


    });

    $(function(){
        $(".search").click(function()
        {
            $.ajax({
                type: 'POST',
                url: "/searchWord" ,
                data:{"word":$("#word").val()},
                dataType: "json",
                success: function(data){
                    $("#answer").text("");
                    if(data["success"]=="true")
                        $("#answer").append(data["chinese"]);
                    else $("#answer").append("词库中没有这个单词，是否单词输入错误!");
                }

            });
        })
    })






};
function insertSystem() {
    $.ajax({
            type: 'get',
            url:'/searchUser',
            dataType: 'json',
            success:function (data) {
                if(data.status == 'success'){
                    username = data.username;
                    window.open(data.userType, '_self')
                }else{
                    alert('请先登陆！！！');
                }
            },
            error:function () {
                alert('请先登陆！！！');
            }
        });
}

