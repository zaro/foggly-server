import React from 'react';
import apiCall from '../common/apicall';

class DomainHeaderRow extends React.Component {
  render() {
    return (
      <tr>
        <th>domain</th>
        <th>application</th>
        <th>created at</th>
        <th>status</th>
        <th>actions</th>
      </tr>
    )
  }
}

class DomainRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      status: props.status,
      state: props.state,
      created: props.created
    };
  }
  startDomain(e) {
    console.log('Starting domain:', this.props.domain);
    this.setState({state: 'starting', status: 'starting'});
    apiCall('/api/domains', {
      'domain': this.props.domain
    }, {method: "POST"}).then((data) => {
      console.log(data);
      this.setState({state: 'up', status: 'running'});
    }).catch((data, error, textStatus) => {
      console.log(textStatus);
      console.log(error);
      this.setState({state: 'error', status: 'error'});
    });
  }
  stopDomain() {
    console.log('Stoping domain:', this.props.domain);
    this.setState({state: 'stopping', status: 'stopping'});
    apiCall('/api/domains', {
      'domain': this.props.domain
    }, {method: "DELETE"}).then((data) => {
      console.log(data);
      this.setState({state: 'down', status: 'stopped'});
    }).catch((data, error, textStatus) => {
      console.log(textStatus);
      console.log(error);
      this.setState({state: 'error', status: 'error'});
    });
  }
  render() {
    let state = _.extend({}, this.props, this.state);
    let color = {
      color: 'brown'
    };
    if (state.state == "up") {
      color = {
        color: "green"
      };
    }
    if (state.state == "down") {
      color = {
        color: "red"
      }
    }
    return (
      <tr style={color}>
        <td>{state.domain}</td>
        <td>{state.type}</td>
        <td>{state.created
            ? new Date(state.created * 1000).toISOString()
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
      domains: [],
      loading: false
    };
  }
  componentDidMount() {
    this.fetch()
  }
  componentWillUnmount() {
    if (this.serverRequest) {
      this.serverRequest.abort();
    }
  }
  fetch() {
    this.serverRequest = apiCall('/api/domains');
    this.setState({loading: true})
    this.serverRequest.then((data) => {
      console.log(data);
      this.setState({domains: data.response, loading: false});
      this.serverRequest = null;
    }).catch((data, errorThrown, textStatus) => {
      console.log(data);
      console.log(textStatus);
      console.log(errorThrown);
      this.setState({loading: false});
      this.serverRequest = null;
    });

  }
  render() {
    var createRow = (domain) => {
      return <DomainRow {...domain} key={domain.domain}/>;
    };
    var spinner;
    if (this.state.loading) {
      spinner = <tr>
        <td colSpan={5} style={{
          textAlign: "center"
        }}>
          <i className='fa fa-spinner fa-3x fa-spin'></i>
        </td>
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
