import React from 'react';
import taskPoll from '../common/taskpoll';

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
            ? new Date(state.created).toISOString()
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

export default
class DomainsTable extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       domains:[],
       loading: false,
     };
 }
 componentDidMount() {
    this.serverRequest = $.ajax('/api/domains',{dataType:'json'});
    this.setState({loading:true})
    this.serverRequest.done((data) =>{
      console.log(data);
      this.setState({
        domains: data.response,
        loading: false
      });
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.log(textStatus);
      console.log(errorThrown);
      this.setState({
        loading: false
      });
    });
  }
  componentWillUnmount() {
    this.serverRequest.abort();
  }
  render() {
    var createRow = (domain) => {
      return <DomainRow {...domain} key={domain.domain}/>;
    };
    var spinner;
    if (this.state.loading){
      spinner = <tr>
        <td colSpan={5} style={{textAlign: "center"}}><i className='fa fa-spinner fa-3x fa-spin'></i></td>
      </tr>;
    }
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
        {spinner}
        {this.state.domains.map(createRow)}
        </tbody>
      </table>
    );
  }
}
