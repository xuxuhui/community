var alloy_setting = {
    // request_url:  "http://localhost",
    request_url:  "http://www.mhlive.top",
    img_host: "http://owgplcxzz.bkt.clouddn.com/"
} 

var SimpoValidate = {

    email: function(value) {
        var reg = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (reg.test(value)) {
            return true;
        } else {
            return false;
        }
    },

    mobile: function(value) {
        var reg = /^1\d{10}$/;
        if (reg.test(value)) {
            return true;
        } else {
            return false;
        }
    },

    password: function(value) {
        if (value.length > 6 && value.length < 12) {
            return true;
        } else {
            return false;
        }
    }
}

var date_util = {
    time: function(dateTimeStamp, exact) {

              var exact = arguments[1] ? arguments[1] : false;
              var minute = 60;
              var hour = minute * 60;
              var day = hour * 24;
              var halfamonth = day * 15;
              var month = day * 30;

              // 当前时间戳
              var now = Math.round(new Date() / 1000);
              // utc偏移
              var d = new Date()
              var localOffset = d.getTimezoneOffset()*60; 
              dateTimeStamp = dateTimeStamp - localOffset;

              var diffValue = now - dateTimeStamp;
              if(diffValue < 0){
               //若日期不符则弹出窗口告之
                return ("结束日期不能小于开始日期！");
              }
              var monthC =diffValue/month;
              var weekC =diffValue/(7*day);
              var dayC =diffValue/day;
              var hourC =diffValue/hour;
              var minC =diffValue/minute;
              // if(monthC>=1){
              //     result= parseInt(monthC) + "月前";
              // }
              if(weekC>=1){
                  if (exact) {
                      var now = new Date(dateTimeStamp * 1000);
                      y = now.getFullYear(),
                      m = now.getMonth() + 1,
                      d = now.getDate();

                      return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + now.toTimeString().substr(0, 8);
                  } else {
                      unixTimestamp = new Date(dateTimeStamp * 1000);
                      result = unixTimestamp.toLocaleDateString();
                  }
                  // result= parseInt(weekC) + "周前";
              }
              else if(dayC>=1){
                  result= parseInt(dayC) +"天前";
              }
              else if(hourC>=1){
                  result= parseInt(hourC) +"小时前";
              }
              else if(minC>=1){
                  result= parseInt(minC) +"分钟前";
              }else {
                  result= "刚刚";
              }
              return result;
        },
    local_date: function(dateTimeStamp) {
              var d = new Date()
              var localOffset = d.getTimezoneOffset()*60; 
              dateTimeStamp = dateTimeStamp - localOffset;
              unixTimestamp = new Date(dateTimeStamp * 1000)

              return unixTimestamp.toLocaleDateString()
        }
}

var url_util = {
    parama: function GetRequest(url) {

            var theRequest = new Object();
            if (url.indexOf("?") != -1) {
                var str = url.substr(1);
                strs = str.split("&");
                for(var i = 0; i < strs.length; i ++) {
                    theRequest[strs[i].split("=")[0]]=(strs[i].split("=")[1]);
                }
            }

            return theRequest;
    }
}
