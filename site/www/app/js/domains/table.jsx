import React from 'react';
import apiCall from '../common/apicall';
import { GenericTable } from '../common/table';
import { Button, ButtonGroup } from 'react-bootstrap';

function DomainHeaderRow() {
  return (
    <tr>
      <th>domain</th>
      <th>application</th>
      <th>created at</th>
      <th>status</th>
      <th>actions</th>
    </tr>
  );
}

class DomainRow extends React.Component {
  static propTypes = {
    _id: React.PropTypes.string.isRequired,
    status: React.PropTypes.string.isRequired,
    state: React.PropTypes.string.isRequired,
    type: React.PropTypes.string.isRequired,
    created: React.PropTypes.string,
    domain: React.PropTypes.string.isRequired,
    removeRow: React.PropTypes.func.isRequired,
    showError: React.PropTypes.func.isRequired,
  }

  constructor(props) {
    super(props);
    this.state = {
      status: props.status,
      state: props.state,
      created: props.created,
    };
  }
  startDomain = () => {
    console.log('Starting domain:', this.props.domain);
    this.setState({ state: 'starting', status: 'starting' });
    apiCall('/api/domains', {
      domain: this.props.domain,
    }, { method: 'POST' }).then((data) => {
      console.log(data);
      this.setState({ state: 'up', status: 'running' });
    }).catch((error) => {
      console.error(error);
      this.setState({ state: 'error', status: 'error' });
    });
  }
  stopDomain = () => {
    console.log('Stoping domain:', this.props.domain);
    this.setState({ state: 'stopping', status: 'stopping' });
    apiCall('/api/domains', {
      domain: this.props.domain,
    }, { method: 'DELETE' }).then((data) => {
      console.log(data);
      this.setState({ state: 'down', status: 'stopped' });
    }).catch((error) => {
      console.error(error);
      this.setState({ state: 'error', status: 'error' });
    });
  }
  destroyDomain = () => {
    console.log('Destroy domain:', this.props.domain);
    this.setState({ working: true });
    apiCall('/api/domains/delete', {
      domain: this.props.domain,
    }, { method: 'POST' }).then((data) => {
      console.info('destroyDomain Done : %o', data);
      this.props.removeRow(this.props._id);
    }).catch((error) => {
      console.error('deleteDatabase Error : %o', error);
      this.props.showError(error);
      this.setState({ working: false });
    });
  }

  render() {
    const state = _.extend({}, this.props, this.state);
    let rowStyle = {
      color: 'brown',
      verticalAlign: 'middle',
    };
    if (state.state === 'up') {
      rowStyle.color = 'green';
    }
    if (state.state === 'down') {
      rowStyle.color = 'red';
    }
    return (
      <tr>
        <td style={rowStyle}>{this.props.domain}</td>
        <td style={rowStyle}>{this.props.type}</td>
        <td style={rowStyle}>{this.props.created
            ? new Date(this.props.created * 1000).toISOString()
            : '-'}</td>
        <td style={rowStyle}>{this.props.status}</td>
        <td>
          <ButtonGroup bsSize="xsmall">
            <Button title="Start domain" onClick={this.startDomain} className="btn-raised" bsStyle="success">start</Button>
            <Button title="Stop domain" onClick={this.stopDomain} className="btn-raised" bsStyle="warning">stop</Button>
            <Button title="Destroy domain" onClick={this.destroyDomain} className="btn-raised" bsStyle="danger">destroy</Button>
          </ButtonGroup>
        </td>
      </tr>
    );
  }
}

export default
class DomainsTable extends GenericTable {
  static defaultProps = {
    headerRowComponent: DomainHeaderRow,
    rowComponent: DomainRow,
    columns: 5,
    showError: React.PropTypes.func.isRequired,
  };
  componentDidMount() {
    this.fetch();
  }
  componentWillUnmount() {
    if (this.serverRequest) {
      this.serverRequest.abort();
    }
  }
  fetch() {
    this.serverRequest = apiCall('/api/domains');
    this.setState({ loading: true });
    this.serverRequest.then((data) => {
      console.log(data);
      const dataList = _.forEach(data.response, (value) => {
        value._id = value.domain;
      });

      this.setState({ dataList, loading: false });
      this.serverRequest = null;
    }).catch((error) => {
      console.error(error);
      this.setState({ loading: false });
      this.serverRequest = null;
    });
  }

}
