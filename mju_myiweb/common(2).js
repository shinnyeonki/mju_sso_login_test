/* 동적으로 컨텐츠 높이 조절 */
function setContentHeight(objSet, objTar){ 
	var objSet   = document.getElementById(objSet); /**/
	var objTarHeight= document.getElementById(objTar).offsetHeight; /**/
	objSet.style.height = objTarHeight + "px";
}


$(document).ready(function() {
	$("._wizOdr").find(" > li:first").addClass("_1st");
	$("._wizOdr").find(" > li:last").addClass("_last");
	$("._wizOdr").find(" > li:odd").addClass("_odd");
	$("._wizOdr").find(" > li:even").addClass("_even");
	$("._wizOdr > li._1st").next("li").addClass("_2nd");
	$("._wizOdr > li._2nd").next("li").addClass("_3rd");
	$("._wizOdr > li.last").prev("li").addClass("_lastPrev");
	
	$("._fnctWrap ._fnTable tbody").find(" > tr:odd").addClass("_odd");
	$("._fnctWrap ._fnTable tbody").find(" > tr:even").addClass("_even");
	
	
	$(".menuUItop > div > ul > li").each(function(i){
		var tempClass = "eQ";
		var num = i+1;
		if(num<10){
			tempClass += "0"+num;
		}else{
			tempClass += num;
		}
		$(this).addClass(tempClass);
	});
	
	$("._fnctWrap").hover(function() {
		$("._fnctAdmin").hide();
		$(this).find("._fnctAdmin").show();
	});
	$("._fnctWrap").mouseleave(function() {
		$("._fnctAdmin").hide();
	});
});



function _autoSubHeight() {
	setContentHeight("_container","_content");
	$(window).on("load resize scroll", function() {
		setContentHeight("_container","_content");
	});
}

/*
$(window).on("load resize scroll", function() {
	setContentHeight("_contentBuilder","_contentBuilder");
});
*/


