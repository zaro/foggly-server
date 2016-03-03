module.exports = function (taskId, debug) {
  return new Promise(function(resolve, reject){
    var doPoll = function(){
      $.ajax('/api/task?id='+taskId,{dataType:'json'})
        .done(function (data) {
          if(debug){
            console.log(data);
          }
          if(data.completed){
            resolve(data);
          } else {
            setTimeout(doPoll, 1000);
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          if(debug){
            console.log(textStatus);
          }
          reject(errorThrown, textStatus);
        });
    };
    doPoll();
  });
};
