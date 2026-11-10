import { useState } from 'react';
import { Button, Stack, TextInput } from '@mantine/core';
import { useUpdateSettings } from '../api/useUpdateSettings';

type Props = { readonly initialName: string };

export const SettingsForm = ({ initialName }: Props) => {
  const [name, setName] = useState(initialName);
  const { mutate, isPending } = useUpdateSettings();

  return (
    <Stack>
      <TextInput label="Display name" value={name} onChange={(e) => setName(e.currentTarget.value)} />
      <Button loading={isPending} onClick={() => mutate({ name })}>
        Sumbit
      </Button>
    </Stack>
  );
};
