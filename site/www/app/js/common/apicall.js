import taskPoll from './taskpoll';

export default function (endPoint, sendData, options) {
  const opts = _.defaults(options, {
    dataType: 'json', method: 'GET',
    contentType: 'application/json; charset=utf-8',
  });
  opts.data = JSON.stringify(sendData);
  let req;
  const p = new Promise((resolve, reject) => {
    req = $.ajax(endPoint, opts).done((data) => {
      if (data.error) {
        reject(data.error);
        return;
      }
      if ('id' in data) {
        taskPoll(data.id).then((taskStatus) => {
          resolve(taskStatus);
        }).catch((error, e1, e2) => {
          reject(error, e1, e2);
        });
      } else {
        resolve(data);
      }
    }).fail((jqXHR) => {
      reject(jqXHR.responseText ? jqXHR.responseText : jqXHR.statusText);
    });
  });
  p.abort = () => {
    req.abort();
  };
  return p;
}
