export default function (taskId) {
  return new Promise((resolve, reject) => {
    const doPoll = () => {
      $.ajax(`/api/task?id=${taskId}`, { dataType: 'json' })
        .done((data) => {
          if (data.completed) {
            if (data.error) {
              reject(data.error);
              return;
            }
            resolve(data);
          } else {
            setTimeout(doPoll, 1000);
          }
        })
        .fail((jqXHR, textStatus, errorThrown) => {
          if (errorThrown) {
            reject(errorThrown);
          } else {
            reject(jqXHR.responseText ? jqXHR.responseText : jqXHR.statusText);
          }
        });
    };
    doPoll();
  });
}
