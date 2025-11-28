$(function(){
	imageEditSet();
});
function imageEditSet(){
			
	$(".dummyImageDataList").remove();
	
	//dummy 생성
	$(".imageDataList").each(function(){
		$(this).removeClass("hidden");
		var html = $(this).outerHTML();
		
		$(this).wrap("<div/>");
		$(this).parent().append("<div class='dummyImageDataList'>" + html + "</div>");
		$(this).unwrap("<div/>");
		
		$(this).addClass("hidden");
	});
	
	
	$(".dummyImageDataList .imageDataList").each(function(){
		var imageType = $(this).attr("class").replace("imageDataList ", "");
		if( imageType.indexOf("thumb") != -1 ){
				
			$(this).wrap("<div class=\"slideImage\" />");
			$(this).parent().append("<p class=\"slideViewer\"></p>");
			$(this).wrap("<div class=\"slideThumb\" />");
			
			$(this).find(" > li").eq(0).addClass("_active");
			$(this).closest(".slideImage").find(".slideViewer").empty().append( $(this).find(" > li").eq(0).html() );
			
			/*
			var aa = $(this).closest(".slideImage").find(".slideViewer").parent(".slideImage").height();
			var bb = $(this).closest(".slideImage").find(".slideViewer").parent(".slideImage").find(".slideThumb").height();
			
			console.log(aa);
			console.log(bb);
			*/
			
			//a 태그 비활성화
			$(this).find("a").click(function(){
				return false;
			});
			
			$(this).find("li img").click(function(){
				$(this).closest(".imageDataList").find("li").removeClass("_active");
				$(this).closest("li").addClass("_active");
				
				$(this).closest(".slideImage").find(".slideViewer").empty().append( $(this).closest("li").html() );
			});
			
		}else if( imageType.indexOf("slide") != -1 ){
			$(this).jshowoff({
				changeSpeed: 100,
				speed:5000,
				animatePause : true,
				autoPlay : true,
				effect : 'fade',
				links : false,
				hoverPause : false,
				controls : true
			});
		}
	});
	
	
}