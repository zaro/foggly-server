import React from 'react';
import apiCall from '../common/apicall';
import { GenericTable } from '../common/table';
import ConfirmDialog from '../common/confirmdialog';
import { Button, ButtonGroup, ButtonToolbar, DropdownButton, MenuItem, Checkbox } from 'react-bootstrap';
import DomainAddPublikKey from './addpublickey';
import InfoDialog from './infodialog';

function DomainHeaderRow() {
  return (
    <tr>
      <th>#</th>
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
    refreshData: React.PropTypes.func.isRequired,
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
    this.setState({ state: 'starting', status: 'starting', working: true });
    apiCall('/api/domains', {
      domain: this.props.domain,
    }, { method: 'POST' }).then((data) => {
      console.log('Started %o', data);
      this.setState({ state: 'up', status: 'running', working: false });
      this.props.refreshData();
    }).catch((error) => {
      console.error('startDomain Error : %o', error);
      this.props.showError(error);
      this.setState({ state: 'error', status: 'error', working: false });
      this.props.refreshData();
    });
  }

  stopDomain = () => {
    console.log('Stoping domain:', this.props.domain);
    this.setState({ state: 'stopping', status: 'stopping', working: true });
    apiCall('/api/domains', {
      domain: this.props.domain,
    }, { method: 'DELETE' }).then((data) => {
      console.log('Stopped %o', data);
      this.setState({ state: 'down', status: 'stopped', working: false });
      this.props.refreshData();
    }).catch((error) => {
      console.error('stopDomain Error : %o', error);
      this.props.showError(error);
      this.setState({ state: 'error', status: 'error', working: false });
      this.props.refreshData();
    });
  }

  recreateDomain = () => {
    console.log('Recreating domain:', this.props.domain);
    this.setState({ working: true, error: null });
    apiCall('/api/domains/recreate', {
      domain: this.props.domain,
    }, { method: 'POST' }).then((data) => {
      console.log('Recreated %o', data);
      this.setState({ working: false });
    }).catch((error) => {
      console.error('recreateDomain Error : %o', error);
      this.props.showError(error);
      this.setState({ state: 'error', status: 'error', working: false });
    });
  }

  moreActions = (eventKey, _event) => {
    this[eventKey]();
  }
  addPublicKey = () => {
    this.refs.addPkDialog.show();
  }
  destroyDomainConfirm = () => {
    this.refs.destroyDomainConfirm.show();
  }
  showDomainInfo = () => {
    this.refs.domainInfoDialog.show();
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
      console.error('destroyDomain Error : %o', error);
      this.props.showError(error);
      this.setState({ working: false });
      this.props.refreshData();
    });
  }

  enableDomainSslDialog = () => {
    this.sslOnly = false;
    this.refs.enableDomainSsl.show();
  }
  enableDomainSsl= () => {
    console.log('Enable ssl for domain:', this.props.domain);
    console.log(this.sslOnly.checked);
    this.setState({ working: true });
    apiCall('/api/domains/ssl', {
      domain: this.props.domain,
      sslOnly: this.sslOnly.checked ? 'yes' : 'no',
    }, { method: 'POST' }).then((data) => {
      console.info('enableDomainSsl Done : %o', data);
      this.setState({ working: false });
    }).catch((error) => {
      console.error('enableDomainSsl Error : %o', error);
      this.props.showError(error);
      this.setState({ working: false });
      this.props.refreshData();
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
    console.log(this.state.worker);
    return (
      <tr>
        <td style={rowStyle}>{this.state.working ? <i className="fa fa-spinner fa-spin"></i> : null}</td>
        <td style={rowStyle}>{this.props.domain}</td>
        <td style={rowStyle}>{_.truncate(this.props.type)}</td>
        <td style={rowStyle}>{this.props.created
            ? new Date(this.props.created).toLocaleString('en-GB')
            : '-'}</td>
        <td style={rowStyle}>{this.props.status}</td>
        <td>
          <ButtonToolbar>
            <ButtonGroup bsSize="xsmall">
              <Button title="Show domain info" onClick={this.showDomainInfo} className="btn-raised" bsStyle="info">info</Button>
            </ButtonGroup>
            <ButtonGroup bsSize="xsmall">
              <Button title="Start domain" onClick={this.startDomain} className="btn-raised" bsStyle="success">start</Button>
              <Button title="Stop domain" onClick={this.stopDomain} className="btn-raised" bsStyle="warning">stop</Button>
            </ButtonGroup>
            <ButtonGroup bsSize="xsmall">
              <DropdownButton title="More actions" id="more-actions" className="btn-raised" onSelect={this.moreActions}>
                <MenuItem eventKey="addPublicKey">Add public key</MenuItem>
                <MenuItem divider />
                <MenuItem eventKey="enableDomainSslDialog">Enable HTTPS</MenuItem>
                <MenuItem eventKey="recreateDomain">Recreate domain</MenuItem>
                <MenuItem divider />
                <MenuItem eventKey="destroyDomainConfirm" bsStyle="warning">Destroy domain</MenuItem>
              </DropdownButton>
            </ButtonGroup>
          </ButtonToolbar>
          <DomainAddPublikKey data={{ domain: this.props.domain }} ref="addPkDialog" title="Add Ssh Public key" />
          <ConfirmDialog danger ref="destroyDomainConfirm" title="All domain data will be deleted!" onSubmit={this.destroyDomain} >
            <p>Are yoy sure you want to destroy this domain?</p>
          </ConfirmDialog>
          <InfoDialog ref="domainInfoDialog" title="Domain information" domain={this.props.domain} />
          <ConfirmDialog ref="enableDomainSsl" title="Enable Domain HTTPS" onSubmit={this.enableDomainSsl} >
            <Checkbox inline inputRef={(ref) => { this.sslOnly = ref; }}>HTTPS Only (will redirect http:// to https://)</Checkbox>
          </ConfirmDialog>
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
