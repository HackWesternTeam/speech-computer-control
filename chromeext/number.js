$(document).ready(()=>{
    // google
    setTimeout(function(){ 
        numberitems("span.S3Uucc");
    }, 1000);

    // youtube
    numberitems("ytd-rich-grid-video-renderer[mini-mode] #video-title.ytd-rich-grid-video-renderer");
    numberitems("ytd-grid-video-renderer #video-title.yt-simple-endpoint.ytd-grid-video-renderer");
    numberitems("#video-title.ytd-video-renderer");
})

function numberitems(str){
    // var a = $("span.S3Uucc")
    var a = $(str)
    var links=[];

    for (let index = 0; index < a.length; index++) {
        const element = a[index].innerHTML;
        a[index].innerHTML = "("+index+"): "+element;
        links.push(a[index].baseURI)
    }
}