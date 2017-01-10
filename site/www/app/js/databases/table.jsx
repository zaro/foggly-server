import React from 'react';
import apiCall from '../common/apicall';
import { GenericTable } from '../common/table';
import { Button, ButtonGroup } from 'react-bootstrap';

function DatabasesHeader() {
  return (
    <tr>
      <th>#</th>
      <th>host</th>
      <th>database</th>
      <th>user</th>
      <th>password</th>
      <th>actions</th>
    </tr>
    );
}


class DatabasesRow extends React.Component {
  static propTypes = {
    _id: React.PropTypes.string.isRequired,
    db_name: React.PropTypes.string.isRequired,
    db_user: React.PropTypes.string.isRequired,
    db_pass: React.PropTypes.string.isRequired,
    host: React.PropTypes.string.isRequired,
    removeRow: React.PropTypes.func.isRequired,
    showError: React.PropTypes.func.isRequired,
    dbType: React.PropTypes.string.isRequired,
  }
  constructor(props) {
    super(props);
    this.state = {
      working: false,
    };
  }
  deleteDatabase = () => {
    console.log('Delete database:', this.props.db_name);
    this.setState({ working: true });
    apiCall(`/api/databases/${this.props.dbType}/delete`, {
      db_name: this.props.db_name,
      db_user: this.props.db_user,
      host: this.props.host,
    }, { method: 'DELETE' }).then((data) => {
      console.info('deleteDatabase Done : %o', data);
      this.props.removeRow(this.props._id);
    }).catch((error) => {
      console.error('deleteDatabase Error : %o', error);
      this.props.showError(error);
      this.setState({ working: false });
    });
  }
  render() {
    const style = {};
    if (this.state.working) {
      style.textDecoration = 'line-through';
    }
    return (
      <tr style={style}>
        <td>{this.state.working ? <i className="fa fa-spinner fa-spin"></i> : null}</td>
        <td>{this.props.host}</td>
        <td>{this.props.db_name}</td>
        <td>{this.props.db_user}</td>
        <td>{this.props.db_pass}</td>
        <td>
          <ButtonGroup bsSize="xsmall">
            <Button title="Delete database" onClick={this.deleteDatabase} className="btn-raised" bsStyle="danger">delete</Button>
          </ButtonGroup>
        </td>
      </tr>
    );
  }
}

export default
class DatabasesTable extends GenericTable {
  static defaultProps = {
    headerRowComponent: DatabasesHeader,
    rowComponent: DatabasesRow,
    columns: 4,
    showError: React.PropTypes.func.isRequired,
    dbType: React.PropTypes.string.isRequired,
  };
  fetch() {
    this.serverRequest = apiCall(`/api/databases/${this.props.dbType}`);
    this.setState({ loading: true });
    this.serverRequest.then((data) => {
      const dataList = _.forEach(data.response, (value) => {
        value._id = value.host + value.db_name + value.db_user;
        value.dbType = this.props.dbType;
      });
      this.setState({ dataList, loading: false });
      this.serverRequest = null;
    }).catch((error) => {
      console.error(error);
      this.props.showError(error);
      this.setState({ loading: false });
      this.serverRequest = null;
    });
  }
  cancelFetch() {
    if (this.serverRequest) {
      this.serverRequest.abort();
    }
  }
}
