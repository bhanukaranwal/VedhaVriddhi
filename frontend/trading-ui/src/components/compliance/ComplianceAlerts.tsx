import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  AlertTitle,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Badge,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Gavel,
  Assignment,
  Close,
  Refresh,
} from '@mui/icons-material';
import { useQuery, useMutation } from 'react-query';
import { formatDate } from '../../utils/formatting';

interface ComplianceAlert {
  alert_id: string;
  rule_id: string;
  rule_name: string;
  violation_type: string;
  severity: 'info' | 'warning' | 'violation' | 'critical';
  description: string;
  portfolio_id?: string;
  transaction_id?: string;
  occurred_at: string;
  status: 'active' | 'investigating' | 'resolved';
  current_value?: number;
  limit_value?: number;
  regulation_source: string;
}

interface ComplianceStatus {
  overall_status: 'compliant' | 'warning' | 'violation';
  active_violations: number;
  critical_violations: number;
  pending_reports: number;
  compliance_score: number;
}

const ComplianceAlerts: React.FC = () => {
  const [selectedAlert, setSelectedAlert] = useState<ComplianceAlert | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch compliance status
  const { data: complianceStatus, isLoading: statusLoading, refetch: refetchStatus } = useQuery<ComplianceStatus>(
    'complianceStatus',
    async () => {
      const response = await fetch('/api/compliance/status');
      return response.json();
    },
    { refetchInterval: 30000 }
  );

  // Fetch active alerts
  const { data: alerts, isLoading: alertsLoading, refetch: refetchAlerts } = useQuery<ComplianceAlert[]>(
    'complianceAlerts',
    async () => {
      const response = await fetch('/api/compliance/alerts');
      return response.json();
    },
    { refetchInterval: 30000 }
  );

  // Acknowledge alert mutation
  const acknowledgeAlertMutation = useMutation(
    async (alertId: string) => {
      const response = await fetch(`/api/compliance/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      return response.json();
    },
    {
      onSuccess: () => {
        refetchAlerts();
        setDialogOpen(false);
      },
    }
  );

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error color="error" />;
      case 'violation':
        return <Warning color="warning" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'info':
        return <Info color="info" />;
      default:
        return <Info color="info" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'violation':
        return 'warning';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'warning':
        return 'warning';
      case 'violation':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleAlertClick = (alert: ComplianceAlert) => {
    setSelectedAlert(alert);
    setDialogOpen(true);
  };

  const handleAcknowledge = () => {
    if (selectedAlert) {
      acknowledgeAlertMutation.mutate(selectedAlert.alert_id);
    }
  };

  const handleRefresh = () => {
    refetchStatus();
    refetchAlerts();
  };

  if (statusLoading || alertsLoading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      {/* Compliance Status Overview */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            Compliance Status
          </Typography>
          <IconButton onClick={handleRefresh}>
            <Refresh />
          </IconButton>
        </Box>

        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" color={getStatusColor(complianceStatus?.overall_status || 'compliant')}>
                  {complianceStatus?.overall_status?.toUpperCase() || 'UNKNOWN'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overall Status
                </Typography>
              </Box>
              
              <Box display="flex" gap={3}>
                <Box textAlign="center">
                  <Typography variant="h5" color="error.main">
                    {complianceStatus?.critical_violations || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Critical
                  </Typography>
                </Box>
                
                <Box textAlign="center">
                  <Typography variant="h5" color="warning.main">
                    {complianceStatus?.active_violations || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Violations
                  </Typography>
                </Box>
                
                <Box textAlign="center">
                  <Typography variant="h5" color="info.main">
                    {complianceStatus?.pending_reports || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Reports
                  </Typography>
                </Box>
                
                <Box textAlign="center">
                  <Typography variant="h5" color="success.main">
                    {complianceStatus?.compliance_score || 100}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Compliance Score
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Active Alerts */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Compliance Alerts
          </Typography>

          {!alerts || alerts.length === 0 ? (
            <Alert severity="success" icon={<CheckCircle />}>
              No active compliance alerts
            </Alert>
          ) : (
            <List>
              {alerts.map((alert) => (
                <ListItem
                  key={alert.alert_id}
                  button
                  onClick={() => handleAlertClick(alert)}
                  sx={{
                    border: '1px solid',
                    borderColor: `${getSeverityColor(alert.severity)}.light`,
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': {
                      backgroundColor: `${getSeverityColor(alert.severity)}.lighter`,
                    },
                  }}
                >
                  <ListItemIcon>
                    <Badge badgeContent={alert.severity === 'critical' ? '!' : null} color="error">
                      {getSeverityIcon(alert.severity)}
                    </Badge>
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {alert.rule_name}
                        </Typography>
                        <Chip
                          label={alert.severity.toUpperCase()}
                          size="small"
                          color={getSeverityColor(alert.severity) as any}
                          variant="outlined"
                        />
                        <Chip
                          label={alert.regulation_source}
                          size="small"
                          icon={<Gavel />}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {alert.description}
                        </Typography>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(alert.occurred_at, 'datetime')}
                          </Typography>
                          {alert.portfolio_id && (
                            <Typography variant="caption" color="text.secondary">
                              Portfolio: {alert.portfolio_id}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Alert Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              {selectedAlert && getSeverityIcon(selectedAlert.severity)}
              <Typography variant="h6">
                {selectedAlert?.rule_name}
              </Typography>
            </Box>
            <IconButton onClick={() => setDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {selectedAlert && (
            <Box>
              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {selectedAlert.description}
                </Typography>
              </Box>

              <Box display="flex" gap={2} mb={2}>
                <Chip
                  label={`Severity: ${selectedAlert.severity.toUpperCase()}`}
                  color={getSeverityColor(selectedAlert.severity) as any}
                  variant="outlined"
                />
                <Chip
                  label={`Source: ${selectedAlert.regulation_source}`}
                  icon={<Gavel />}
                  variant="outlined"
                />
                <Chip
                  label={`Status: ${selectedAlert.status.toUpperCase()}`}
                  variant="outlined"
                />
              </Box>

              {(selectedAlert.current_value !== undefined && selectedAlert.limit_value !== undefined) && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Values
                  </Typography>
                  <Typography variant="body2">
                    Current: {selectedAlert.current_value.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">
                    Limit: {selectedAlert.limit_value.toLocaleString()}
                  </Typography>
                </Box>
              )}

              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Details
                </Typography>
                <Typography variant="body2">
                  Rule ID: {selectedAlert.rule_id}
                </Typography>
                <Typography variant="body2">
                  Violation Type: {selectedAlert.violation_type}
                </Typography>
                <Typography variant="body2">
                  Occurred: {formatDate(selectedAlert.occurred_at, 'datetime')}
                </Typography>
                {selectedAlert.portfolio_id && (
                  <Typography variant="body2">
                    Portfolio: {selectedAlert.portfolio_id}
                  </Typography>
                )}
                {selectedAlert.transaction_id && (
                  <Typography variant="body2">
                    Transaction: {selectedAlert.transaction_id}
                  </Typography>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Close
          </Button>
          {selectedAlert?.status === 'active' && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleAcknowledge}
              disabled={acknowledgeAlertMutation.isLoading}
            >
              {acknowledgeAlertMutation.isLoading ? 'Acknowledging...' : 'Acknowledge'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComplianceAlerts;
