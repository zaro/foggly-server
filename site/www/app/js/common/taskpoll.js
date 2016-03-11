export default function (taskId) {
  return new Promise(function(resolve, reject){
    var doPoll = function(){
      $.ajax('/api/task?id='+taskId,{dataType:'json'})
        .done(function (data) {
          if(data.completed){
            if(data.response.error){
              reject(data);
              return;
            }
            resolve(data);
          } else {
            setTimeout(doPoll, 1000);
          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          if(debug){
            console.log(textStatus);
          }
          reject(null, errorThrown, textStatus);
        });
    };
    doPoll();
  });
};
