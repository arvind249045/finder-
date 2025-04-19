import React, { useState } from 'react';
import { Box, Button, Container, Heading, Input, VStack, Text, Progress, useToast } from '@chakra-ui/react';

export default function App() {
  const [domain, setDomain] = useState('');
  const [status, setStatus] = useState('Idle');
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const toast = useToast();

  const handleRun = async () => {
    if (!domain) {
      toast({ title: 'Please enter a domain name.', status: 'warning' });
      return;
    }
    setStatus('Processing...');
    setLoading(true);
    setEmails([]);
    setProgress(0);

    // SSE logic (pseudo, replace with real logic)
    const evtSource = new EventSource(`/run_harvester?domain=${encodeURIComponent(domain)}`);
    evtSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.progress) setProgress(data.progress);
        if (data.emails) setEmails(data.emails);
        if (data.status) setStatus(data.status);
      } catch {}
    };
    evtSource.addEventListener('final_data', (event) => {
      setLoading(false);
      setStatus('Completed');
      try {
        const results = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        setEmails(results.emails || []);
      } catch {}
      evtSource.close();
    });
    evtSource.onerror = () => {
      setLoading(false);
      setStatus('Error');
      toast({ title: 'Error connecting to server.', status: 'error' });
      evtSource.close();
    };
  };

  return (
    <Container centerContent py={10}>
      <VStack spacing={6} w="100%" maxW="md">
        <Heading>Better Harvester</Heading>
        <Input
          placeholder="Enter domain (e.g., example.com)"
          value={domain}
          onChange={e => setDomain(e.target.value)}
          isDisabled={loading}
        />
        <Button colorScheme="orange" onClick={handleRun} isLoading={loading} w="100%">
          Run Harvester
        </Button>
        <Box w="100%">
          <Text>Status: {status}</Text>
          {loading && <Progress value={progress} size="sm" colorScheme="orange" mt={2} />}
        </Box>
        {emails.length > 0 && (
          <Box w="100%" bg="gray.50" p={4} borderRadius="md" boxShadow="md">
            <Heading size="md" mb={2}>Results</Heading>
            <VStack align="start" spacing={1}>
              {emails.map((email, i) => (
                <Text key={i}>{email}</Text>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>
    </Container>
  );
}
