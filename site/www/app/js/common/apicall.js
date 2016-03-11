import taskPoll from './taskpoll';

export default function (endPoint, data, opts) {
  opts = _.defaults(opts, {
        dataType:'json', method: "GET",
        contentType: "application/json; charset=utf-8",
      });
  opts.data = JSON.stringify(data)
  let p = new Promise(function(resolve, reject){
    let req = $.ajax(endPoint, opts).done((data) =>{
      if(data.error){
        reject(data);
        return;
      }
      if(data.id){
        taskPoll(data.id).then((taskStatus)=>{
          resolve(data)
        }).catch((error, e1, e2)=>{
          reject(error, e1, e2)
        });
      } else {
        resolve(data);
      }
    }).fail((jqXHR, textStatus, errorThrown) => {
      reject(null,  errorThrown, textStatus);
    });;
  });
  p.abort = function(){
    req.abort();
  }
  return p;
};
