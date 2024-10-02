import React, { useState } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Grid,
} from '@mui/material';
import { makeStyles } from '@mui/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    padding: '16px',
    backgroundColor: '#f5f5f5',
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px', // Increased space between the header and the search bar
  },
  form: {
    marginBottom: '24px',
  },
  button: {
    backgroundColor: '#1976d2',
    color: '#fff',
    '&:hover': {
      backgroundColor: '#115293',
    },
    margin: '10px',
  },
  tableContainer: {
    maxWidth: '400px', // Adjust the max-width of the table
    margin: 'auto', // Center the table
  },
  table: {
    minWidth: 300, // Adjust the min-width of the table
  },
  tableHeader: {
    backgroundColor: '#1976d2',
  },
  tableHeaderCell: {
    color: '#fff',
    fontWeight: 'bold',
  },
  loader: {
    marginTop: '16px',
  },
  error: {
    color: 'red',
    marginTop: '16px',
  },
  compactCell: {
    padding: '8px',
  },
  sectionTitle: {
    color: '#1976d2',
  },
  resultContainer: {
    textAlign: 'left', // Aligning to the left for consistency
    marginTop: '20px',
  },
}));

function App() {
  const classes = useStyles();
  const [date, setDate] = useState('');
  const [startLocation, setStartLocation] = useState('');
  const [endLocation, setEndLocation] = useState('');
  const [tripCounts, setTripCounts] = useState([]);
  const [cheapestHour, setCheapestHour] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTripCounts = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`http://localhost:8000/api/trip-count/?date=${date}`);
      setTripCounts(response.data);
    } catch (err) {
      setError('Error fetching trip counts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCheapestHour = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`http://localhost:8000/api/cheapest-hour/?start_location=${startLocation}&end_location=${endLocation}&date=${date}`);
      setCheapestHour(response.data);
    } catch (err) {
      setError('Error fetching cheapest hour. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className={classes.root}>
      <Typography variant="h3" className={classes.header}>
        Yellow Cab Trip Data Analysis
      </Typography>

      <Grid container spacing={2} alignItems="center" justifyContent="center" className={classes.form}>
        <Grid item>
          <TextField
            type="date"
            label="Date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </Grid>
        <Grid item>
          <Button
            className={classes.button}
            onClick={fetchTripCounts}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Get Trip Counts'}
          </Button>
        </Grid>
        <Grid item>
          <TextField
            label="Start Location ID"
            value={startLocation}
            onChange={(e) => setStartLocation(e.target.value)}
          />
        </Grid>
        <Grid item>
          <TextField
            label="End Location ID"
            value={endLocation}
            onChange={(e) => setEndLocation(e.target.value)}
          />
        </Grid>
        <Grid item>
          <Button
            className={classes.button}
            onClick={fetchCheapestHour}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Get Cheapest Hour'}
          </Button>
        </Grid>
      </Grid>

      {error && <Typography className={classes.error}>{error}</Typography>}

      {loading && <CircularProgress className={classes.loader} />}

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <TableContainer component={Paper} className={classes.tableContainer}>
            <Table className={classes.table} aria-label="trip counts table">
              <TableHead className={classes.tableHeader}>
                <TableRow>
                  <TableCell className={classes.tableHeaderCell}>Hour</TableCell>
                  <TableCell align="right" className={classes.tableHeaderCell}>Count</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tripCounts.map((trip) => (
                  <TableRow key={trip.hour}>
                    <TableCell component="th" scope="row" className={classes.compactCell}>
                      {trip.hour}
                    </TableCell>
                    <TableCell align="right" className={classes.compactCell}>{trip.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
        <Grid item xs={12} md={6} className={classes.resultContainer}>
          {cheapestHour && (
            <div>
              <Typography variant="h6">Cheapest Hour: {cheapestHour.hour}</Typography>
              <Typography>
                Minimum Fare: ${cheapestHour.min_fare !== undefined ? cheapestHour.min_fare.toFixed(2) : 'N/A'}
              </Typography>
            </div>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
