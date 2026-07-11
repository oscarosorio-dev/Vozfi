import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ConversationFeedback } from '@/components/voice/ConversationFeedback';
import { MicButton } from '@/components/voice/MicButton';
import { VoiceStatusIndicator } from '@/components/voice/VoiceStatusIndicator';
import { TransactionRow } from '@/components/finance/TransactionRow';
import { useThemeColor } from '@/hooks/use-theme-color';
import { useVoicePipeline } from '@/hooks/useVoicePipeline';
import { useBalance } from '@/hooks/useBalance';
import { useTransactions } from '@/hooks/useTransactions';
import { useDeleteTransaction } from '@/hooks/useDeleteTransaction';

export default function HomeScreen() {
  const { status, isRecording, result, error, start, stop } = useVoicePipeline();
  const { data: balance, isLoading: isLoadingBalance } = useBalance();
  const { data: transactions, isLoading: isLoadingTxs } = useTransactions();
  const deleteTransaction = useDeleteTransaction();

  const cardColor = useThemeColor({}, 'card');
  const mutedColor = useThemeColor({}, 'muted');
  const incomeColor = useThemeColor({}, 'income');
  const expenseColor = useThemeColor({}, 'expense');
  const borderColor = useThemeColor({}, 'border');

  function handleMicPress() {
    if (isRecording) {
      stop();
    } else {
      start();
    }
  }

  // Obtenemos únicamente las 3 transacciones más recientes para el feed del footer
  const recentTransactions = transactions?.slice(0, 3) ?? [];

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <ScrollView 
        contentContainerStyle={styles.container} 
        showsVerticalScrollIndicator={false}
      >
        {/* Header: Vozfi + Balance Neto Minimalista */}
        <View style={styles.header}>
          <View>
            <ThemedText type="title">Vozfi</ThemedText>
            <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Asistente de voz</ThemedText>
          </View>

          <View style={styles.headerBalance}>
            <ThemedText style={[styles.balanceLabel, { color: mutedColor }]}>Balance Neto</ThemedText>
            {isLoadingBalance ? (
              <ThemedText style={{ color: mutedColor, fontSize: 15 }}>Cargando...</ThemedText>
            ) : (
              <ThemedText
                type="defaultSemiBold"
                style={[
                  styles.balanceAmount,
                  { color: (balance?.balance ?? 0) >= 0 ? incomeColor : expenseColor }
                ]}
              >
                ${(balance?.balance ?? 0).toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </ThemedText>
            )}
          </View>
        </View>

        {/* Sección Central: Micrófono, Estados y Feedback de conversación */}
        <View style={styles.micSection}>
          <MicButton status={status} onPress={handleMicPress} />
          <VoiceStatusIndicator status={status} errorMessage={error} />
          <ConversationFeedback result={result} />
        </View>

        {/* Footer: Breve historial de lo último registrado */}
        <View style={styles.historySection}>
          <ThemedText type="defaultSemiBold" style={styles.historyTitle}>
            Últimos movimientos
          </ThemedText>

          {isLoadingTxs ? (
            <ThemedText style={[styles.stateText, { color: mutedColor }]}>
              Cargando movimientos...
            </ThemedText>
          ) : recentTransactions.length === 0 ? (
            <ThemedText style={[styles.stateText, { color: mutedColor }]}>
              Sin movimientos registrados aún.
            </ThemedText>
          ) : (
            <View
              style={[
                styles.historyList,
                { backgroundColor: cardColor, borderColor, borderWidth: StyleSheet.hairlineWidth }
              ]}
            >
              {recentTransactions.map((tx) => (
                <TransactionRow
                  key={tx.id}
                  transaction={tx}
                  onDelete={(id) => deleteTransaction.mutate(id)}
                />
              ))}
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
    gap: 36,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
  },
  headerBalance: {
    alignItems: 'flex-end',
  },
  balanceLabel: {
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  balanceAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 2,
  },
  micSection: {
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
    width: '100%',
    minHeight: 180,
  },
  historySection: {
    width: '100%',
    gap: 12,
  },
  historyTitle: {
    fontSize: 15,
    letterSpacing: 0.3,
  },
  historyList: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  stateText: {
    textAlign: 'center',
    marginVertical: 16,
    fontSize: 14,
  },
});