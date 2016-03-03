var React = require('react')
var taskPoll = require('./taskpoll')

class DomainRow extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       status: props.status,
       state: props.state,
       created: props.created,
     };
  }
  startDomain(e) {
    console.log('Starting domain:', this.props.domain);
    this.setState({
      state:'starting',
      status:'starting',
    });
    $.ajax('/api/domains',{
          dataType:'json',method: "POST",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify({'domain': this.props.domain})}).done((data) =>{
      console.log(data);
      if(data.error){
        console.error(data.error);
        return;
      }
      if(data.id){
        taskPoll(data.id).then((taskStatus)=>{
          console.log(taskStatus);
          this.setState({
            state:'up',
            status:'running',
          });
        });
      } else {
        console.error('WTF:',data);
      }
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.log(textStatus);
      console.log(errorThrown);
      this.setState({
        state:'error',
        status:'error',
      });
    });;
  }
  stopDomain() {
    console.log('Stoping domain:', this.props.domain);
    this.setState({
      state:'stopping',
      status:'stopping',
    });
    $.ajax('/api/domains',{
          dataType:'json',method: "DELETE",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify({'domain': this.props.domain})}).done((data) =>{
      console.log(data);
      if(data.error){
        console.error(data.error);
        return;
      }
      if(data.id){
        taskPoll(data.id).then((taskStatus)=>{
          console.log(taskStatus);
          this.setState({
            state:'down',
            status:'stopped',
          });
        });
      } else {
        console.error('WTF:',data);
      }
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.log(textStatus);
      console.log(errorThrown);
      this.setState({
        state:'error',
        status:'error',
      });
    });;
  }
  render() {
    let state = _.extend({},this.props, this.state);
    let color = {color: 'brown'};
    if(state.state == "up"){
      color = {color: "green"};
    }
    if(state.state == "down"){
      color = {color: "red"}
    }
    return (
      <tr style={color}>
        <td>{state.domain}</td>
        <td>{state.type}</td>
        <td>{state.created
            ? new Date(state.created).toString()
            : '-'}</td>
        <td>{state.status}</td>
        <td>
          <a className="btn btn-raised btn-primary btn-xs" title="Start domain" href="#" onClick={(e) => this.startDomain(e)}>start</a>
          <a className="btn btn-raised btn-primary btn-xs" title="Stop domain" href="#" onClick={(e) => this.stopDomain(e)}>stop</a>
        </td>
      </tr>
    );
  }
}

class DomainsTable extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       domains:[]
     };
 }
 componentDidMount() {
    this.serverRequest = $.ajax('/api/domains',{dataType:'json'});
    this.serverRequest.done((data) =>{
      console.log(data);
      this.setState({
        domains: data.response
      });
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.log(textStatus);
      console.log(errorThrown);
    });
  }
  componentWillUnmount() {
    this.serverRequest.abort();
  }
  render() {
    var createRow = (domain) => {
      return <DomainRow {...domain} key={domain.domain}/>;
    };
    return (
      <table className="table table-striped" id="domainsTable">
        <thead>
          <tr>
            <th>domain</th>
            <th>application</th>
            <th>created at</th>
            <th>status</th>
            <th>actions</th>
          </tr>
        </thead>
        <tbody>
        {this.state.domains.map(createRow)}
        </tbody>
      </table>
    );
  }
}

module.exports = DomainsTable

var ReactDom =  require('react-dom');
var el = document.getElementById('domains-table');
ReactDom.render(<DomainsTable />, el);
