/*===================================
@ common
===================================*/
var common = {	
	stage : { width : 0 , height : 0 , top : 0 } ,
	headerElement : null,
	leftElement : null,
	init : function(){	
		
		this.headerElement = $('#header');
		this.leftElement = $('.left-menu-wrap');
		
		//왼쪽메뉴 총 갯수 설정
		$('.left-menu-list').find('> li').each(function(){
			var totalNum = $(this).find('.snb-list > li').length;
			$(this).find('.btn-left-one .total').html(totalNum);
		});

		//왼쪽메뉴 토글 클릭 이벤트
		$(document).on('click', '.btn-left-one' ,function(){
			common.leftMenuToggle($(this));
		});

		//전체 메뉴 클릭 이벤트
		$(document).on('click' , '.btn-gnb-menu-toggle' , function(){
			common.gnbToggle();
		});
		
		//메인 탭 컨텐츠
		$(document).on('click' , '.main-community-tab .btn-tab-nav' , function(){
			$('.main-community').find('.main-community-tab .tab-cell').eq($(this).parent().index()).addClass('actived').siblings().removeClass('actived');
			$('.main-community-data').find('.tab-data').eq($(this).parent().index()).addClass('actived').siblings().removeClass('actived');
		});
		
		//상단 이동
		$(document).on('click' , '.btn-page-top' , function(){
			$('html, body').stop().animate({'scrollTop':0}, {queue:false, duration:350, easing:'easeOutCubic'});
		});
		
		//챗봇 닫기버튼
		$(document).on('click', '#iconclose', function(){
			$(".chatbotarea").css("visibility", "hidden");
		})

		this.resize();
		this.scroll();
	},	
	gnbToggle : function(){
		if(common.headerElement.hasClass('actived')){
			common.headerElement.removeClass('actived');
			common.leftElement.removeClass('actived');
			$('html').removeClass('fix');
		}else{
			common.headerElement.addClass('actived');
			common.leftElement.addClass('actived');
			$('html').addClass('fix');
		}
	},

	leftMenuToggle : function( item ){
		var parentsElement = item.parents('.left-menu-list');

		parentsElement.find('> li').each(function(){
			if($(this).index() == item.parent().index()){
				if($(this).hasClass('open')){
					$(this).removeClass('open');
				}else{
					$(this).addClass('open');
				}
			}else{
				$(this).removeClass('open');
			}
		});
	},
	ready : function(){		
		
	},
	load : function(){
		
	},
	resize : function(){				
		common.stage.width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
		common.stage.height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
		common.stage.top = window.scrollTop || document.documentElement.scrollTop || document.body.scrollTop;

		if(common.stage.width > 1024){
			if(common.headerElement.hasClass('actived')){
				common.headerElement.removeClass('actived');
				common.leftElement.removeClass('actived');
				$('html').removeClass('fix');
			}
			if(common.headerElement.hasClass('scroll')) {
				common.headerElement.removeClass('scroll');
				common.leftElement.removeClass('scroll');
			}
		}else{

		}
	},
	scroll : function(){
		common.stage.top = window.scrollTop || document.documentElement.scrollTop || document.body.scrollTop;		

		if(common.stage.width <= 1024){
			if($('#container').length > 0 ){
				if(common.stage.top >= $('#container').offset().top){
					common.headerElement.addClass('scroll');
					common.leftElement.addClass('scroll');
				}else{
					common.headerElement.removeClass('scroll');
					common.leftElement.removeClass('scroll');
				}
			}
		}
	}
};

var popIndex = 99999;
var popElement = null;

function popOpen( _id ){
	popIndex++;
	popElement = $('#' + _id);
	popElement.addClass('actived').css({'z-index' : popIndex});
	$('html').addClass('fix');
}

function popClose( _item ){
	if(_item){
		$(_item).removeClass('actived');
	}else{
		popElement.removeClass('actived');
	}
	popElement = null;
	$('html').removeClass('fix');
}

function popClose_iframe(){
	parent.popElement.removeClass('actived');
	parent.popElement = null;
	parent.$('html').removeClass('fix');
}


/*===================================
@ Device
===================================*/
var device = {
	// 브라우저 종류 체크
	// device.isMobile();
	isMobile : function(){
		return (navigator.userAgent.match(/iPhone|iPad|iPod|Android|Windows CE|BlackBerry|Symbian|Windows Phone|webOS|Opera Mini|Opera Mobi|POLARIS|IEMobile|lgtelecom|nokia|SonyEricsson/i) != null || navigator.userAgent.match(/LG|SAMSUNG|Samsung/) != null);
	},
	// 아이패드 프로 체크
	// device.isIpadPro();
	isIpadPro : function(){
		return (/iPhone|iPod/.test(navigator.platform) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) && !window.MSStream;
	},
	// 익스 구버전 체크
	// device.isIE();
	isIE : function(){
		return (navigator.appName == 'Netscape' && navigator.userAgent.search('Trident') != -1) || (navigator.userAgent.toLowerCase().indexOf('msie') != -1);
	}
};

window.addEventListener('DOMContentLoaded' , common.ready);
window.addEventListener('load' , common.load);
window.addEventListener('resize' , common.resize);
window.addEventListener('scroll' , common.scroll);

(function(){	
	if(device.isMobile()) $('html').addClass('mobile');
})();

$(document).ready(function(){
	common.init();
	$(document).on('click' , '.layer-pop-wrap' , function(e){
		if($(e.target).parents('.pop-data').length == 0){					
			popClose();
		}
	});
});

//로딩 이미지 생성 : common.css와 연계
//20221124 -> pure javascript로 변경
function activeLoadingScreen(){
	
	let loadingScreen = document.getElementById("myLoading");
	let notIos = (navigator.userAgent.match(/iPhone|iPad|iPod/) == null);
	
	//submit중임을 명시하는 screen 생성 : 기존에 화면에 별도로 설정된게 있다면 생성하지 않는다. + ios에서는 띄우지 않는다.
	if(loadingScreen == null && notIos){
		let loadingDivParent = document.createElement("div");
		loadingDivParent.id = "myLoading";
		loadingDivParent.style.display = "block";
		
		let loadingDivChild = document.createElement("div");
		loadingDivChild.id = "loading";
		loadingDivChild.className = "actived";
		
		let loadingDivChildWrap = document.createElement("div");
		loadingDivChildWrap.className = "loading-wrap";
		
		let loadingDivChildWrapTxt = document.createElement("div");
		loadingDivChildWrapTxt.className = "txt";
		loadingDivChildWrapTxt.innerText = "Loading";
		
		let loadingDivChildWrapBar = document.createElement("div");
		loadingDivChildWrapBar.className = "bar";
		
		loadingDivChildWrap.append(loadingDivChildWrapTxt);
		loadingDivChildWrap.append(loadingDivChildWrapBar);
		
		loadingDivChild.append(loadingDivChildWrap);
		loadingDivParent.append(loadingDivChild);
		
		document.body.append(loadingDivParent);
		
	} else if(loadingScreen != null && notIos) {
		loadingScreen.style.display = "block";
	}
	
	//submit중임을 명시하는 screen 생성 : 기존에 화면에 별도로 설정된게 있다면 생성하지 않는다. (Jquery Version)
	/*
	if($("div#loading").length <= 0){
		$("body").append($("<div>").prop({id : "myLoading"}).css({
			"display" : "block"
		}).append($("<div>").prop({id : "loading"}).addClass("actived")
				.append($("<div>").addClass("loading-wrap")
						.append($("<div>").addClass("txt").html("Loading"))
						.append($("<div>").addClass("bar"))
						)
				)
		);
	} else {
		$("div#myLoading").css({"display" : "block"});
	}
	*/
}

//로딩스크린 제거
function deactiveLoadingScreen(){
	let loadingScreen = document.getElementById("myLoading");
	if(loadingScreen != null){
		loadingScreen.style.display = "none";
	}
	
}